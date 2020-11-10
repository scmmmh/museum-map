import click
import inflection
import json
import os
import requests

from collections import Counter
from lxml import etree
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ..models import Base, Item, Group


@click.command()
@click.pass_context
def generate_groups(ctx):
    """Generate the basic groups."""
    engine = create_engine(ctx.obj['config'].get('db', 'uri'))
    Base.metadata.bind = engine
    dbsession = sessionmaker(bind=engine)()
    categories = []
    query = dbsession.query(Item).filter(Item.group_id == None)
    for item in query:
        for category in item.attributes['categories']:
            categories.append(category.lower())
    counts = Counter(categories)
    with click.progressbar(query, length=query.count(), label='Generating groups') as progress:
        for item in progress:
            for category in item.attributes['categories']:
                category = category.lower()
                if counts[category] >= 30:
                    group = dbsession.query(Group).filter(Group.value == category).first()
                    if group is None:
                        group = Group(value=category, label=category[0].upper() + category[1:])
                        dbsession.add(group)
                    item.group = group
                    break
    dbsession.commit()


def strip_article(text):
    if text.startswith('a '):
        return text[2:]
    elif text.startswith('an '):
        return text[3:]
    else:
        return text


def apply_nlp(category):
    """Recursively apply the NLP processing rules."""
    if ' ' in category:
        if ' for ' in category:
            idx = category.find(' for ')
            prefix = strip_article(category[:idx])
            suffix = strip_article(category[idx + 5:])
            return [suffix, prefix] + apply_nlp(suffix) + apply_nlp(prefix)
        elif '(' in category:
            start = category.find('(')
            end = category.find(')')
            outer = strip_article((category[:start].strip() + ' ' + category[end + 1:].strip()).strip())
            inner = strip_article(category[start + 1:end].strip())
            return [outer, inner] + apply_nlp(outer) + apply_nlp(inner)
        elif ' with ' in category:
            idx = category.find(' with ')
            prefix = strip_article(category[:idx])
            suffix = strip_article(category[idx + 6:])
            return [prefix, suffix] + apply_nlp(prefix) + apply_nlp(suffix)
        elif ' of ' in category:
            idx = category.find(' of ')
            prefix = strip_article(category[:idx].strip())
            suffix = strip_article(category[idx + 4:].strip())
            if prefix in ['pair', 'copy', 'base', 'fragments', 'figure', 'copy']:
                return [suffix] + apply_nlp(suffix)
            else:
                return [suffix, prefix] + apply_nlp(suffix) + apply_nlp(prefix)
        elif ' from ' in category:
            idx = category.find(' from ')
            prefix = strip_article(category[:idx].strip())
            suffix = strip_article(category[idx + 4:].strip())
            if prefix in ['pair', 'copy', 'base', 'fragments', 'figure', 'copy']:
                return [suffix] + apply_nlp(suffix)
            else:
                return [suffix, prefix] + apply_nlp(suffix) + apply_nlp(prefix)
        elif '&' in category:
            categories = [strip_article(c.strip()) for c in category.split('&')]
            for cat in list(categories):
                categories = categories + apply_nlp(cat)
            return categories
        elif ' and ' in category or ',' in category:
            categories = []
            while ' and ' in category or ',' in category:
                and_idx = category.find(' and ')
                comma_idx = category.find(',')
                if and_idx >= 0 and comma_idx >= 0:
                    idx = min(and_idx, comma_idx)
                elif and_idx >= 0:
                    idx = and_idx
                elif comma_idx >= 0:
                    idx = comma_idx
                else:
                    idx = -1
                if idx >= 0:
                    categories.append(strip_article(category[:idx].strip()))
                    if category[idx] == ',':
                        category = category[idx + 1:].strip()
                    else:
                        category = category[idx + 5:].strip()
            if category.strip():
                categories.append(strip_article(category.strip()))
            for cat in list(categories):
                categories = categories + apply_nlp(cat)
            return categories
        elif ' or ' in category:
            categories = []
            while ' or ' in category:
                idx = category.find(' or ')
                if idx >= 0:
                    categories.append(strip_article(category[:idx].strip()))
                    category = category[idx + 4:].strip()
            if category.strip():
                categories.append(strip_article(category.strip()))
            for cat in list(categories):
                categories = categories + apply_nlp(cat)
            return categories
        else:
            categories = category.split()
            return [' '.join(categories[-idx:]) for idx in range(len(categories) - 1, 0, -1)]
    else:
        return []


def apply_aat(category):
    """Expand the category using the AAT."""
    if os.path.exists('aat.json'):
        with open('aat.json') as in_f:
            cache = json.load(in_f)
    else:
        cache = {}
    if category in cache:
        data = cache[category]
    else:
        cache[category] = []
        response = requests.get('http://vocabsservices.getty.edu/AATService.asmx/AATGetTermMatch',
                                params=[('term', f'"{category}"'),
                                        ('logop', 'and'),
                                        ('notes', '')])
        if response.status_code == 200:
            hierarchies = etree.fromstring(response.content).xpath('Subject/Preferred_Parent/text()')
            cat_hierarchies = []
            for hierarchy in hierarchies:
                categories = []
                for entry in hierarchy.split(',')[1:]:
                    entry = entry.strip().lower()
                    if ' by ' in entry:
                        continue
                    if '(' in entry:
                        entry = entry[:entry.find('(')].strip()
                    if '[' in entry:
                        entry = entry[:entry.find('[')].strip()
                    if 'facet' in entry:
                        entry = entry[:-6]
                    entry = inflection.singularize(entry)
                    if entry not in categories:
                        categories.append(entry)
                cat_hierarchies.append(categories)
            if len(cat_hierarchies) > 1:
                merged = []
                added = True
                while added:
                    added = False
                    for hierarchy in cat_hierarchies:
                        if hierarchy:
                            item = hierarchy.pop()
                            added = True
                            if item not in merged:
                                merged.append(item)
                merged.reverse()
                cache[category] = merged
            elif len(cat_hierarchies) == 1:
                cache[category] = cat_hierarchies[0]
    with open('aat.json', 'w') as out_f:
        json.dump(cache, out_f)
    return cache[category]


@click.command()
@click.pass_context
def expand_categories(ctx):
    """Expand the object categories."""
    engine = create_engine(ctx.obj['config'].get('db', 'uri'))
    Base.metadata.bind = engine
    dbsession = sessionmaker(bind=engine)()
    query = dbsession.query(Item).filter(Item.group_id == None)
    with click.progressbar(query, length=query.count(), label='Expanding categories') as progress:
        for item in progress:
            categories = [c.lower() for c in item.attributes['object']]
            for category in item.attributes['object']:
                categories = categories + apply_nlp(category.lower())
            for category in list(categories):
                categories = categories + apply_aat(category)
            item.attributes['categories'] = categories
    dbsession.commit()


@click.group()
def processing():
    """Process the loaded data."""
    pass


processing.add_command(generate_groups)
processing.add_command(expand_categories)
