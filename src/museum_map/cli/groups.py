import click
import inflection
import math

from collections import Counter
from numpy import array
from scipy.spatial.distance import cosine
from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker

from .items import apply_aat, apply_nlp
from ..models import Base, Group, Item


def generate_groups_impl(ctx):
    engine = create_engine(ctx.obj['config'].get('db', 'uri'))
    Base.metadata.bind = engine
    dbsession = sessionmaker(bind=engine)()
    query = dbsession.query(Item).filter(Item.group_id == None)
    categories = []
    for item in query:
        for category in item.attributes['categories']:
            categories.append(category.lower())
    counts = [(cat, count) for cat, count in Counter(categories).most_common() if count >= 15]
    counts.sort(key=lambda c: c[1])
    max_groups = len(counts)
    with click.progressbar(length=max_groups, label='Generating groups') as progress:
        while counts:
            category = counts[0][0]
            group = dbsession.query(Group).filter(Group.value == category).first()
            if group is None:
                group = Group(value=category, label=category[0].upper() + category[1:])
                dbsession.add(group)
            for item in query:
                if category in item.attributes['categories']:
                    item.group = group
            dbsession.commit()
            categories = []
            for item in query:
                for category in item.attributes['categories']:
                    categories.append(category.lower())
            old_counts = len(counts)
            counts = [(cat, count) for cat, count in Counter(categories).most_common() if count >= 15]
            counts.sort(key=lambda c: c[1])
            progress.update(old_counts - len(counts))
    dbsession.commit()


@click.command()
@click.pass_context
def generate_groups(ctx):
    """Generate the basic groups."""
    generate_groups_impl(ctx)


def fill_vector(group):
    vec = array([0 for _ in range(0, 300)], dtype=float)
    for dim, value in group.attributes['lda_vector']:
        vec[dim] = value
    return vec


def split_by_similarity(dbsession, group):
    vectors = {}
    sorted_items = []
    current = group.items[0]
    vectors[current.id] = fill_vector(current)
    while len(sorted_items) < len(group.items):
        next_item = None
        next_sim = None
        for item in group.items:
            if item in sorted_items:
                continue
            if item.id not in vectors:
                vectors[item.id] = fill_vector(item)
            if not next_item or cosine(vectors[current.id], vectors[item.id]) > next_sim:
                next_item = item
                next_sim = cosine(vectors[current.id], vectors[item.id])
        if next_item:
            sorted_items.append(next_item)
    limit = len(group.items) / math.ceil(len(group.items) / 100)
    new_group = Group(value=group.value, label=group.label, parent=group)
    count = 0
    for item in sorted_items:
        if count > limit:
            new_group = Group(value=group.value, label=group.label, parent=group)
            count = 0
        item.group = new_group
        count = count + 1


def split_by_attribute(dbsession, group, attr):
    values = []
    for item in group.items:
        if attr in item.attributes and item.attributes[attr]:
            values.extend(item.attributes[attr])
    categories = [(v, c) for v, c in Counter(values).most_common() if c < len(group.items) * 0.6666 and c >= 15]
    if categories:
        category_values = [v for v, _ in categories]
        has_values = 0
        for item in group.items:
            found = False
            for value in item.attributes[attr]:
                if value in category_values:
                    found = True
                    break
            if found:
                has_values = has_values + 1
        if has_values / len(group.items) > 0.9:
            categories.reverse()
            for category in categories:
                new_group = Group(value=category[0], label=f'{group.label} - {category[0]}', parent=group)
                dbsession.add(new_group)
                for item in list(group.items):
                    if category[0] in item.attributes[attr]:
                        item.group = new_group
            new_group = Group(value=group.label, label=group.label, parent=group)
            dbsession.add(new_group)
            for item in list(group.items):
                item.group = new_group
            return True
    return False


def split_by_year(dbsession, group):
    years = []
    decades = []
    centuries = []
    with_year = 0
    for item in group.items:
        if item.attributes['year_start']:
            years.append(item.attributes['year_start'])
            with_year = with_year + 1
    if with_year / len(group.items) > 0.95:
        common = [(int(v), c) for v, c in Counter(years).most_common()]
        start_year = min([c for c, _ in common])
        end_year = max([c for c, _ in common])
        if (start_year != end_year):
            year_boundaries = []
            if (end_year - start_year) <= 100 and (end_year - start_year) > 10:
                start_decade = math.floor(start_year / 10)
                end_decade = math.floor(end_year / 10)
                decades = []
                for start_year in range(start_decade * 10, (end_decade + 1) * 10, 10):
                    for item in list(group.items):
                        if item.attributes['year_start']:
                            if start_year <= int(item.attributes['year_start']) and int(item.attributes['year_start']) < start_year + 10:
                                if len(decades) == 0 or decades[-1][0][0] != start_year:
                                    decades.append([[start_year], 1])
                                else:
                                    decades[-1][1] = decades[-1][1] + 1
                idx = 0
                while idx < len(decades) - 1:
                    if decades[idx][1] + decades[idx + 1][1] < 100:
                        decades[idx][0].extend(decades[idx + 1][0])
                        decades[idx][1] = decades[idx][1] + decades[idx + 1][1]
                        decades.pop(idx + 1)
                    else:
                        idx = idx + 1
                for years, _ in decades:
                    new_group = None
                    for item in list(group.items):
                        if item.attributes['year_start']:
                            if years[0] <= int(item.attributes['year_start']) and int(item.attributes['year_start']) < years[-1] + 10:
                                if new_group is None:
                                    if len(years) == 1:
                                        label = f'{years[0]}s'
                                    else:
                                        label = f'{years[0]}s-{years[-1]}s'
                                    new_group = Group(value=str(start_year), label=f'{group.label} - {label}', parent=group)
                                    dbsession.add(new_group)
                                item.group = new_group
                if group.items:
                    new_group = Group(value=group.label, label=group.label, parent=group)
                    dbsession.add(new_group)
                    for item in list(group.items):
                        item.group = new_group
                return True
            elif (end_year - start_year) > 100:
                start_century = math.floor(start_year / 100)
                end_century = math.floor(end_year / 100)
                centuries = []
                for start_year in range(start_century * 100, (end_century + 1) * 100, 100):
                    century = math.floor(start_year / 100) + 1
                    if century % 10 == 1 and century != 11:
                        label = f'{century}st'
                    elif century % 10 == 2 and century != 12:
                        label = f'{century}nd'
                    elif century % 10 == 3 and century != 13:
                        label = f'{century}rd'
                    else:
                        label = f'{century}th'
                    for item in list(group.items):
                        if item.attributes['year_start']:
                            if start_year <= int(item.attributes['year_start']) and int(item.attributes['year_start']) < start_year + 100:
                                if len(centuries) == 0 or centuries[-1][0][0] != label:
                                    centuries.append([[label], 1])
                                else:
                                    centuries[-1][1] = centuries[-1][1] + 1
                idx = 0
                while idx < len(centuries) - 1:
                    if centuries[idx][1] + centuries[idx + 1][1] < 100:
                        centuries[idx][0].extend(centuries[idx + 1][0])
                        centuries[idx][1] = centuries[idx][1] + centuries[idx + 1][1]
                        centuries.pop(idx + 1)
                    else:
                        idx = idx + 1
                for years, _ in centuries:
                    new_group = None
                    for item in list(group.items):
                        if item.attributes['year_start']:
                            century = math.floor(int(item.attributes['year_start']) / 100) + 1
                            if century % 10 == 1 and century != 11:
                                label = f'{century}st'
                            elif century % 10 == 2 and century != 12:
                                label = f'{century}nd'
                            elif century % 10 == 3 and century != 13:
                                label = f'{century}rd'
                            else:
                                label = f'{century}th'
                            if label in years[0]:
                                if new_group is None:
                                    if len(years) == 1:
                                        group_label = years[0]
                                    else:
                                        group_label = f'{years[0]}-{years[-1]}'
                                    new_group = Group(value=str(start_year), label=f'{group.label} - {group_label} century', parent=group)
                                    dbsession.add(new_group)
                                item.group = new_group
                if group.items:
                    new_group = Group(value=group.label, label=group.label, parent=group)
                    dbsession.add(new_group)
                    for item in list(group.items):
                        item.group = new_group
                return True
    return False


def split_large_groups_impl(ctx):
    engine = create_engine(ctx.obj['config'].get('db', 'uri'))
    Base.metadata.bind = engine
    dbsession = sessionmaker(bind=engine)()
    splitting = True
    anim = ['|', '/', '-', '\\']
    click.echo('Splitting large groups  ', nl=False)
    while splitting:
        splitting = False
        for group in dbsession.query(Group):
            if len(group.children) == 0:
                click.echo(f'\b{anim[-1]}', nl=False)
                anim.insert(0, anim.pop())
                if len(group.items) > 120 and len(group.items) < 300:
                    if split_by_year(dbsession, group):
                        splitting = True
                    else:
                        split_by_similarity(dbsession, group)
                        splitting = True
                elif len(group.items) >= 300:
                    if split_by_attribute(dbsession, group, 'concepts'):
                        splitting = True
                    elif split_by_attribute(dbsession, group, 'subjects'):
                        splitting = True
                    elif split_by_attribute(dbsession, group, 'materials'):
                        splitting = True
                    elif split_by_attribute(dbsession, group, 'techniques'):
                        splitting = True
                    elif split_by_year(dbsession, group):
                        splitting = True
                    else:
                        split_by_similarity(dbsession, group)
                        splitting = True
        dbsession.commit()
    click.echo('\b ')


@click.command()
@click.pass_context
def split_large_groups(ctx):
    """Split large groups into smaller ones."""
    split_large_groups_impl(ctx)


def merge_singular_plural_impl(ctx):
    engine = create_engine(ctx.obj['config'].get('db', 'uri'))
    Base.metadata.bind = engine
    dbsession = sessionmaker(bind=engine)()
    modifying = True
    anim = ['|', '/', '-', '\\']
    click.echo('Merging singular and plural  ', nl=False)
    while modifying:
        click.echo(f'\b{anim[-1]}', nl=False)
        anim.insert(0, anim.pop())
        modifying = False
        for group in dbsession.query(Group):
            other = dbsession.query(Group).filter(and_(Group.value == inflection.singularize(group.value),
                                                       Group.id != group.id)).first()
            if other:
                for item in list(other.items):
                    item.group = group
                    dbsession.add(item)
                dbsession.delete(other)
                dbsession.commit()
                modifying = True
                break
    click.echo('\b ')


@click.command()
@click.pass_context
def merge_singular_plural(ctx):
    """Merge singular and plural groups."""
    merge_singular_plural_impl(ctx)


def add_parent_groups_impl(ctx):
    engine = create_engine(ctx.obj['config'].get('db', 'uri'))
    Base.metadata.bind = engine
    dbsession = sessionmaker(bind=engine)()
    query = dbsession.query(Group).filter(Group.parent_id == None)
    with click.progressbar(query, length=query.count(), label='Adding parent groups') as progress:
        for group in progress:
            categories = apply_aat(group.value, merge=False)
            if categories:
                for category_list in categories:
                    mapped = False
                    for category in category_list:
                        parent_group = dbsession.query(Group).filter(Group.value == category).first()
                        if not parent_group:
                            parent_group = Group(value=category, label=category[0].upper() + category[1:])
                            dbsession.add(group)
                        group.parent = parent_group
                        mapped = True
                        group = parent_group
                        if group.parent_id:
                            break
                    if mapped:
                        break
            else:
                mapped = False
                for category in apply_nlp(group.value):
                    parent_group = dbsession.query(Group).filter(Group.value == category).first()
                    if not parent_group:
                        parent_group = dbsession.query(Group).filter(Group.value == inflection.pluralize(category)).first()
                    if parent_group:
                        group.parent = parent_group
                        dbsession.commit()
                        mapped = True
                        break
                if not mapped:
                    if group.value not in ['styles and periods']:
                        for category in apply_nlp(group.value):
                            hierarchies = apply_aat(category, merge=False)
                            groups = []
                            for hierarchy in hierarchies:
                                if group.value not in hierarchy:
                                    for potential_group in dbsession.query(Group).filter(Group.value.in_(hierarchy)):
                                        depth = 0
                                        tmp = potential_group
                                        while tmp:
                                            depth = depth + 1
                                            tmp = tmp.parent
                                        groups.append((potential_group, depth, len(potential_group.items)))
                            if groups:
                                groups.sort(key=lambda g: (g[1], g[2]), reverse=True)
                                group.parent = groups[0][0]
                                break
    dbsession.commit()


@click.command()
@click.pass_context
def add_parent_groups(ctx):
    """Add any required parent groups."""
    add_parent_groups_impl(ctx)


def prune_single_groups_impl(ctx):
    engine = create_engine(ctx.obj['config'].get('db', 'uri'))
    Base.metadata.bind = engine
    dbsession = sessionmaker(bind=engine)()
    anim = ['|', '/', '-', '\\']
    click.echo('Pruning single groups  ', nl=False)
    pruning = True
    while pruning:
        pruning = False
        for group in dbsession.query(Group):
            click.echo(f'\b{anim[-1]}', nl=False)
            anim.insert(0, anim.pop())
            if len(group.items) == 0 and len(group.children) == 1:
                group.children[0].parent = group.parent
                dbsession.delete(group)
                dbsession.commit()
                pruning = True
                break
    click.echo('\b ')


@click.command()
@click.pass_context
def prune_single_groups(ctx):
    """Remove groups that have a single child and no items."""
    prune_single_groups_impl(ctx)


def move_inner_items_impl(ctx):
    engine = create_engine(ctx.obj['config'].get('db', 'uri'))
    Base.metadata.bind = engine
    dbsession = sessionmaker(bind=engine)()
    anim = ['|', '/', '-', '\\']
    click.echo('Moving inner items  ', nl=False)
    moving = True
    while moving:
        moving = False
        for group in dbsession.query(Group):
            click.echo(f'\b{anim[-1]}', nl=False)
            anim.insert(0, anim.pop())
            if len(group.items) > 0 and len(group.children) > 0:
                sub_group = Group(value=group.value, label=group.label)
                dbsession.add(sub_group)
                sub_group.parent = group
                for item in list(group.items):
                    item.group = sub_group
                dbsession.commit()
                moving = True
                break
    dbsession.commit()
    click.echo('\b ')


@click.command()
@click.pass_context
def move_inner_items(ctx):
    """Move items from non-leaf groups into extra leaf groups."""
    move_inner_items_impl(ctx)


@click.command()
@click.pass_context
def pipeline(ctx):
    """Run the group processing pipeline."""
    generate_groups_impl(ctx)
    merge_singular_plural_impl(ctx)
    add_parent_groups_impl(ctx)
    prune_single_groups_impl(ctx)
    move_inner_items_impl(ctx)
    split_large_groups_impl(ctx)


@click.group()
def groups():
    """Group generation."""
    pass


groups.add_command(generate_groups)
groups.add_command(split_large_groups)
groups.add_command(add_parent_groups)
groups.add_command(merge_singular_plural)
groups.add_command(prune_single_groups)
groups.add_command(move_inner_items)
groups.add_command(pipeline)
