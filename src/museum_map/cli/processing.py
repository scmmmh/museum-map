import click
import inflection
import json
import math
import os
import requests

from collections import Counter
from lxml import etree
from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker

from ..models import Base, Item, Group


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
                    if ' genre' in entry:
                        entry = entry[:entry.find(' genre')].strip()
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


@click.command()
@click.pass_context
def split_large_groups(ctx):
    """Split large groups into smaller ones."""
    engine = create_engine(ctx.obj['config'].get('db', 'uri'))
    Base.metadata.bind = engine
    dbsession = sessionmaker(bind=engine)()
    # Split sub-categories between 30 and 100
    for group in dbsession.query(Group):
        if len(group.items) > 100:
            moved = True
            while moved:
                moved = False
                categories = []
                for item in group.items:
                    cats = set()
                    cats.update([v.lower() for v in item.attributes['techniques']])
                    cats.update([v.lower() for v in item.attributes['materials']])
                    cats.update([v.lower() for v in item.attributes['subjects']])
                    cats.update([v.lower() for v in item.attributes['concepts']])
                    categories.extend(cats)
                for cat, size in Counter(categories).most_common():
                    if size >= 30 and size <= 100:
                        sub_group = dbsession.query(Group).filter(and_(Group.value == cat,
                                                                       Group.parent_id == group.id)).first()
                        if not sub_group:
                            sub_group = Group(value=cat, label=cat[0].upper() + cat[1:], parent_id=group.id)
                            dbsession.add(sub_group)
                        for item in group.items:
                            cats = set()
                            cats.update([v.lower() for v in item.attributes['techniques']])
                            cats.update([v.lower() for v in item.attributes['materials']])
                            cats.update([v.lower() for v in item.attributes['subjects']])
                            cats.update([v.lower() for v in item.attributes['concepts']])
                            if cat in cats:
                                item.group = sub_group
                                dbsession.add(item)
                        dbsession.commit()
                        moved = True
                        break
    # Merge < 30 categories
    for group in dbsession.query(Group):
        if len(group.items) > 100:
            moved = True
            while moved:
                moved = False
                categories = []
                for item in group.items:
                    cats = set()
                    cats.update([v.lower() for v in item.attributes['techniques']])
                    cats.update([v.lower() for v in item.attributes['materials']])
                    cats.update([v.lower() for v in item.attributes['subjects']])
                    cats.update([v.lower() for v in item.attributes['concepts']])
                    categories.extend(cats)
                new_group = None
                new_count = 0
                for cat, size in Counter(categories).most_common():
                    if size < 30:
                        if not new_group:
                            new_group = Group(value=group.value, label=group.label, parent_id=group.id)
                            dbsession.add(group)
                        for item in group.items:
                            cats = set()
                            cats.update([v.lower() for v in item.attributes['techniques']])
                            cats.update([v.lower() for v in item.attributes['materials']])
                            cats.update([v.lower() for v in item.attributes['subjects']])
                            cats.update([v.lower() for v in item.attributes['concepts']])
                            if cat in cats:
                                item.group = new_group
                                new_count = new_count + 1
                                dbsession.add(item)
                                moved = True
                        if new_count > 100:
                            break
                dbsession.commit()
    # Split large topics by larger categories
    for group in dbsession.query(Group):
        if len(group.items) > 100:
            moved = True
            while moved:
                moved = False
                categories = []
                for item in group.items:
                    cats = set()
                    cats.update([v.lower() for v in item.attributes['techniques']])
                    cats.update([v.lower() for v in item.attributes['materials']])
                    cats.update([v.lower() for v in item.attributes['subjects']])
                    cats.update([v.lower() for v in item.attributes['concepts']])
                    categories.extend(cats)
                for cat, size in Counter(categories).most_common():
                    if size < len(group.items) / 2:
                        sub_group = Group(value=cat, label=cat[0].upper() + cat[1:], parent_id=group.id)
                        for item in group.items:
                            cats = set()
                            cats.update([v.lower() for v in item.attributes['techniques']])
                            cats.update([v.lower() for v in item.attributes['materials']])
                            cats.update([v.lower() for v in item.attributes['subjects']])
                            cats.update([v.lower() for v in item.attributes['concepts']])
                            if cat in cats:
                                item.group = sub_group
                                dbsession.add(item)
                        dbsession.commit()
                        moved = True
                        break
    # Split by year
    for group in dbsession.query(Group):
        if len(group.items) > 100:
            years = []
            for item in group.items:
                if item.attributes['year_start']:
                    years.append(item.attributes['year_start'])
            common = Counter(years).most_common()
            if math.ceil(len(group.items) / 100) < len(common):
                common.sort(key=lambda i: int(i[0]))
                groups = [[[], 0]]
                target_size = len(group.items) / math.ceil(len(group.items) / 100)
                for cat, count in common:
                    if groups[-1][1] + count < target_size:
                        groups[-1][0].append(cat)
                        groups[-1][1] = groups[-1][1] + count
                    else:
                        groups.append([[cat], count])
                if len(groups[-1][0]) == 1:
                    groups[-2][0].extend(groups[-1][0])
                    groups[-2][1] = groups[-2][1] + groups[-1][1]
                    groups = groups[0:-1]
                for cat, _ in groups:
                    if len(cat) == 1:
                        new_group = Group(value=cat[0], label=cat[0], parent_id=group.id)
                    else:
                        label = f'{cat[0]} - {cat[-1]}'
                        new_group = Group(value=label, label=label, parent_id=group.id)
                    dbsession.add(new_group)
                    for item in group.items:
                        if item.attributes['year_start']:
                            if item.attributes['year_start'] in cat:
                                item.group = new_group
                                dbsession.add(item)
                dbsession.commit()


@click.command()
@click.pass_context
def add_parent_groups(ctx):
    """Add any required parent groups."""
    engine = create_engine(ctx.obj['config'].get('db', 'uri'))
    Base.metadata.bind = engine
    dbsession = sessionmaker(bind=engine)()
    for group in dbsession.query(Group).filter(Group.parent_id == None):
        cats = apply_aat(group.value)
        if cats:
            for category in cats:
                parent_group = dbsession.query(Group).filter(Group.value == category).first()
                if parent_group:
                    group.parent_id = parent_group.id
                    break
        else:
            for category in apply_nlp(group.value):
                parent_group = dbsession.query(Group).filter(Group.value == category).first()
                if parent_group:
                    group.parent_id = parent_group.id
                    break
    dbsession.commit()


@click.group()
def processing():
    """Process the loaded data."""
    pass


processing.add_command(expand_categories)
processing.add_command(generate_groups)
processing.add_command(split_large_groups)
processing.add_command(add_parent_groups)
