"""Item processing CLI commands."""

import asyncio
import json
import os

import requests
from bertopic import BERTopic
from lxml import etree
from rich.progress import Progress
from sqlalchemy import func
from sqlalchemy.future import select
from typer import Typer

from museum_map.models import Item, async_sessionmaker
from museum_map.settings import settings

group = Typer(help="Item processing commands")


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


async def expand_categories_impl():
    """Expand the object categories."""
    async with async_sessionmaker() as dbsession:
        count = await dbsession.execute(select(func.count(Item.id)))
        result = await dbsession.execute(select(Item))
        with Progress() as progress:
            task = progress.add_task("Expanding categories", total=count.scalar_one())
            for item in result.scalars():
                categories = [c.lower() for c in item.attributes[settings.data.hierarchy.field]]
                if "nlp" in settings.data.hierarchy.expansions:
                    for category in item.attributes[settings.data.hierarchy.field]:
                        categories = categories + apply_nlp(category.lower())
                if "aat" in settings.data.hierarchy.expansions:
                    for category in list(categories):
                        categories = categories + apply_aat(category)
                item.attributes["_categories"] = categories
                progress.update(task, advance=1)
        await dbsession.commit()


@group.command()
def expand_categories():
    """Expand the object categories."""
    asyncio.run(expand_categories_impl())


async def generate_topic_vectors_impl():
    """Generate topic vectors for all items."""
    topic_model = BERTopic()
    documents = []
    with Progress() as progress:
        async with async_sessionmaker() as dbsession:
            count = (await dbsession.execute(select(func.count(Item.id)))).scalar_one()
            result = await dbsession.execute(select(Item))
            task = progress.add_task("Loading items", total=count)
            for item in result.scalars():
                text = []
                for field in settings.data.topic_fields:
                    if field in item.attributes and item.attributes[field].strip() != "":
                        if item.attributes[field].endswith("."):
                            text.append(item.attributes[field])
                        else:
                            text.append(f"{item.attributes[field]}.")
                documents.append(" ".join(text))
                progress.update(task, advance=1)
        task = progress.add_task("Generating topic model", total=None)
        topic_model.fit(documents)
        progress.update(task, total=1, completed=1)
        topics = topic_model.get_topics()
        progress.update(task, total=1, completed=1)
        async with async_sessionmaker() as dbsession:
            count = (await dbsession.execute(select(func.count(Item.id)))).scalar_one()
            result = await dbsession.execute(select(Item))
            task = progress.add_task("Calculating topic vectors", total=count)
            for item in result.scalars():
                text = []
                for field in settings.data.topic_fields:
                    if field in item.attributes and item.attributes[field].strip() != "":
                        if item.attributes[field].endswith("."):
                            text.append(item.attributes[field])
                        else:
                            text.append(f"{item.attributes[field]}.")
                topic_ids, probabilities = topic_model.transform([" ".join(text)])
                topic_vector = [0.0 for _ in range(0, len(topics))]
                for topic_id, probability in zip(topic_ids, probabilities):
                    if topic_id >= 0 and topic_id < len(topic_vector):
                        topic_vector[int(topic_id)] = float(probability)
                item.attributes["lda_vector"] = topic_vector
                progress.update(task, advance=1)
            await dbsession.commit()


@group.command()
def generate_topic_vectors():
    """Generate topic vectors for all items."""
    asyncio.run(generate_topic_vectors_impl())


async def pipeline_impl():
    """Run the items processing pipeline."""
    await expand_categories_impl()
    await generate_topic_vectors_impl()


@group.command()
def pipeline():
    """Run the items processing pipeline."""
    asyncio.run(pipeline_impl())
