"""Item processing CLI commands."""
import asyncio
import json
import os

import click
import requests
import spacy
# from gensim import corpora, models
from lxml import etree
from sqlalchemy import func
from sqlalchemy.future import select

from museum_map.cli.util import ClickIndeterminate
from museum_map.models import Item, async_sessionmaker


async def tokenise_impl(config):
    """Generate token lists for each item."""
    nlp = spacy.load("en_core_web_sm")
    async with async_sessionmaker() as dbsession:
        count = await dbsession.execute(select(func.count(Item.id)))
        result = await dbsession.execute(select(Item))
        with click.progressbar(result.scalars(), length=count.scalar_one(), label="Tokenising items") as progress:
            for item in progress:
                text = ""
                for field in config["data"]["topic_fields"]:
                    if field in item.attributes and item.attributes[field].strip():
                        if item.attributes[field].strip().endswith("."):
                            text = f"{text} {item.attributes[field].strip()}"
                        else:
                            text = f"{text} {item.attributes[field].strip()}."
                item.attributes["_tokens"] = [t.lemma_ for t in nlp(text) if t.pos_ not in ["PUNCT", "SPACE"]]
        await dbsession.commit()


@click.command()
def tokenise():
    """Generate token lists for each item."""
    asyncio.run(tokenise_impl())


def strip_article(text):
    """Strip any indefinite article from the beginning of the text."""
    text = text.strip()
    if text.startswith("a "):
        return text[2:].strip().strip("()[]")
    elif text.startswith("an "):
        return text[3:].strip().strip("()[]")
    else:
        return text.strip("()[]")


def apply_nlp(category):
    """Recursively apply the NLP processing rules."""
    if " " in category:
        if " for " in category:
            idx = category.find(" for ")
            prefix = strip_article(category[:idx])
            suffix = strip_article(category[idx + 5 :])
            return [suffix, prefix, *apply_nlp(suffix), *apply_nlp(prefix)]
        elif "(" in category:
            start = category.find("(")
            end = category.find(")")
            outer = strip_article(category[:start] + " " + category[end + 1 :])
            inner = strip_article(category[start + 1 : end])
            return [outer, inner, *apply_nlp(outer), *apply_nlp(inner)]
        elif " with " in category:
            idx = category.find(" with ")
            prefix = strip_article(category[:idx])
            suffix = strip_article(category[idx + 6 :])
            return [prefix, suffix, *apply_nlp(prefix), *apply_nlp(suffix)]
        elif " of " in category:
            idx = category.find(" of ")
            prefix = strip_article(category[:idx])
            suffix = strip_article(category[idx + 4 :])
            if prefix in ["pair", "copy", "base", "fragments", "figure", "copy"]:
                return [suffix, *apply_nlp(suffix)]
            else:
                return [suffix, prefix, *apply_nlp(suffix), *apply_nlp(prefix)]
        elif " from " in category:
            idx = category.find(" from ")
            prefix = strip_article(category[:idx])
            suffix = strip_article(category[idx + 4 :])
            if prefix in ["pair", "copy", "base", "fragments", "figure", "copy"]:
                return [suffix, *apply_nlp(suffix)]
            else:
                return [suffix, prefix, *apply_nlp(suffix), *apply_nlp(prefix)]
        elif "&" in category:
            categories = [strip_article(c) for c in category.split("&")]
            for cat in list(categories):
                categories = categories + apply_nlp(cat)
            return categories
        elif " and " in category or "," in category:
            categories = []
            while " and " in category or "," in category:
                and_idx = category.find(" and ")
                comma_idx = category.find(",")
                if and_idx >= 0 and comma_idx >= 0:
                    idx = min(and_idx, comma_idx)
                elif and_idx >= 0:
                    idx = and_idx
                elif comma_idx >= 0:
                    idx = comma_idx
                else:
                    idx = -1
                if idx >= 0:
                    categories.append(strip_article(category[:idx]))
                    if category[idx] == ",":
                        category = category[idx + 1 :]
                    else:
                        category = category[idx + 5 :]
            if category.strip().strip("()[]"):
                categories.append(strip_article(category.strip().strip("()[]")))
            for cat in list(categories):
                categories = categories + apply_nlp(cat)
            return categories
        elif " or " in category:
            categories = []
            while " or " in category:
                idx = category.find(" or ")
                if idx >= 0:
                    categories.append(strip_article(category[:idx]))
                    category = category[idx + 4 :].strip().strip("()[]")
            if category.strip().strip("()[]"):
                categories.append(strip_article(category))
            for cat in list(categories):
                categories = categories + apply_nlp(cat)
            return categories
        else:
            categories = category.split()
            return [" ".join(categories[-idx:]) for idx in range(len(categories) - 1, 0, -1)]
    else:
        return []


def apply_aat(category, merge=True):  # noqa: FBT002
    """Expand the category using the AAT."""
    if os.path.exists("aat.json"):
        with open("aat.json") as in_f:
            cache = json.load(in_f)
    else:
        cache = {}
    if category not in cache:
        cache[category] = []
        response = requests.get(
            "http://vocabsservices.getty.edu/AATService.asmx/AATGetTermMatch",
            params=[("term", f'"{category}"'), ("logop", "and"), ("notes", "")],
            timeout=300,
        )
        if response.status_code == 200:  # noqa: PLR2004
            subjects = etree.fromstring(response.content).xpath("Subject/Subject_ID/text()")  # noqa: S320
            hierarchies = []
            for subject in subjects:
                response2 = requests.get(
                    "http://vocabsservices.getty.edu/AATService.asmx/AATGetSubject",
                    params=[("subjectID", subject)],
                    timeout=300,
                )
                if response.status_code == 200:  # noqa: PLR2004
                    hierarchy_text = etree.fromstring(response2.content).xpath("Subject/Hierarchy/text()")  # noqa: S320
                    if hierarchy_text:
                        hierarchy = []
                        for entry in [h.strip() for h in hierarchy_text[0].split("|") if "<" not in h]:
                            entry = entry.lower()  # noqa: PLW2901
                            if "(" in entry:
                                entry = entry[: entry.find("(")].strip()  # noqa: PLW2901
                            if entry.endswith(" facet"):
                                entry = entry[: entry.find(" facet")].strip()  # noqa: PLW2901
                            if entry.endswith(" genres"):
                                entry = entry[: entry.find(" genres")].strip()  # noqa: PLW2901
                            if entry not in hierarchy:
                                hierarchy.append(entry)
                        hierarchies.append(hierarchy)
            cache[category] = hierarchies
            for hierarchy in hierarchies:
                for start in range(0, len(hierarchy)):
                    if hierarchy[start] not in cache:
                        if hierarchy[start + 1 :]:
                            cache[hierarchy[start]] = [hierarchy[start + 1 :]]
                        else:
                            cache[hierarchy[start]] = []
        with open("aat.json", "w") as out_f:
            json.dump(cache, out_f)
    if merge:
        if len(cache[category]) > 1:
            merged = []
            added = True
            while added:
                added = False
                for hierarchy in cache[category]:
                    if hierarchy:
                        item = hierarchy.pop()
                        added = True
                        if item not in merged:
                            merged.append(item)
            merged.reverse()
            return merged
        elif len(cache[category]) == 1:
            return cache[category][0]
        return []
    else:
        return cache[category]


async def expand_categories_impl(config):
    """Expand the object categories."""
    async with async_sessionmaker() as dbsession:
        count = await dbsession.execute(select(func.count(Item.id)))
        result = await dbsession.execute(select(Item))
        with click.progressbar(result.scalars(), length=count.scalar_one(), label="Expanding categories") as progress:
            for item in progress:
                categories = [c.lower() for c in item.attributes[config["data"]["hierarchy"]["field"]]]
                if "nlp" in config["data"]["hierarchy"]["expansions"]:
                    for category in item.attributes[config["data"]["hierarchy"]["field"]]:
                        categories = categories + apply_nlp(category.lower())
                if "aat" in config["data"]["hierarchy"]["expansions"]:
                    for category in list(categories):
                        categories = categories + apply_aat(category)
                item.attributes["_categories"] = categories
        await dbsession.commit()


@click.command()
@click.pass_context
def expand_categories(ctx):
    """Expand the object categories."""
    asyncio.run(expand_categories_impl(ctx.obj["config"]))


async def generate_topic_vectors_impl():
    """Generate topic vectors for all items."""
    async with async_sessionmaker() as dbsession:

        async def texts(dictionary=None, label=""):
            count = await dbsession.execute(select(func.count(Item.id)))
            result = await dbsession.execute(select(Item))
            with click.progressbar(result.scalars(), length=count.scalar_one(), label=label) as progress:
                for item in progress:
                    if "_tokens" in item.attributes:
                        if dictionary:
                            yield dictionary.doc2bow(item.attributes["_tokens"])
                        else:
                            yield item.attributes["_tokens"]

        dictionary = corpora.Dictionary()
        async for tokens in texts(label="Generating dictionary"):
            dictionary.add_documents([tokens])
        dictionary.filter_extremes(keep_n=None)
        corpus = []
        async for bow in texts(dictionary=dictionary, label="Generating corpus"):
            corpus.append(bow)
        waiting = ClickIndeterminate("Generating model")
        waiting.start()
        model = models.LdaModel(corpus, num_topics=300, id2word=dictionary, update_every=0)
        waiting.stop()
        count = await dbsession.execute(select(func.count(Item.id)))
        result = await dbsession.execute(select(Item))
        with click.progressbar(
            result.scalars(), length=count.scalar_one(), label="Generating topic vectors"
        ) as progress:
            for item in progress:
                if "_tokens" in item.attributes:
                    vec = model[dictionary.doc2bow(item.attributes["_tokens"])]
                    item.attributes["lda_vector"] = [(wid, float(prob)) for wid, prob in vec]
        await dbsession.commit()


@click.command()
def generate_topic_vectors():
    """Generate topic vectors for all items."""
    asyncio.run(generate_topic_vectors_impl())


async def pipeline_impl():
    """Run the items processing pipeline."""
    await expand_categories_impl()
    await tokenise_impl()
    await generate_topic_vectors_impl()


@click.command()
def pipeline():
    """Run the items processing pipeline."""
    asyncio.run(pipeline_impl())


@click.group()
def items():
    """Process the loaded items."""
    pass


items.add_command(tokenise)
items.add_command(expand_categories)
items.add_command(generate_topic_vectors)
items.add_command(pipeline)
