import click
import inflection

from collections import Counter
from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker

from .items import apply_aat, apply_nlp
from ..models import Base, Group, Item


@click.command()
@click.pass_context
def generate_groups(ctx):
    """Generate the basic groups."""
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
def split_large_groups(ctx):
    """Split large groups into smaller ones."""
    engine = create_engine(ctx.obj['config'].get('db', 'uri'))
    Base.metadata.bind = engine
    dbsession = sessionmaker(bind=engine)()
    """# Split sub-categories between 30 and 100
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
                    if cat.strip().strip('()[]') and size < len(group.items) / 2:
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
    """


@click.command()
@click.pass_context
def merge_singular_plural(ctx):
    """Merge singular and plural groups."""
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
def add_parent_groups(ctx):
    """Add any required parent groups."""
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
def prune_single_groups(ctx):
    """Remove groups that have a single child and no items."""
    engine = create_engine(ctx.obj['config'].get('db', 'uri'))
    Base.metadata.bind = engine
    dbsession = sessionmaker(bind=engine)()
    anim = ['|', '/', '-', '\\']
    click.echo('Pruning single groups  ', nl=False)
    pruning = True
    while pruning:
        click.echo(f'\b{anim[-1]}', nl=False)
        anim.insert(0, anim.pop())
        pruning = False
        for group in dbsession.query(Group):
            if len(group.items) == 0 and len(group.children) == 1:
                group.children[0].parent = group.parent
                dbsession.delete(group)
                dbsession.commit()
                pruning = True
                break
    click.echo('\b ')


@click.command()
@click.pass_context
def move_inner_items(ctx):
    """Move items from non-leaf groups into extra leaf groups."""
    engine = create_engine(ctx.obj['config'].get('db', 'uri'))
    Base.metadata.bind = engine
    dbsession = sessionmaker(bind=engine)()
    anim = ['|', '/', '-', '\\']
    click.echo('Moving inner items  ', nl=False)
    moving = True
    while moving:
        click.echo(f'\b{anim[-1]}', nl=False)
        anim.insert(0, anim.pop())
        moving = False
        for group in dbsession.query(Group):
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
