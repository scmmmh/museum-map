import asyncio
import click
import inflection
import math

from collections import Counter
from numpy import array
from scipy.spatial.distance import cosine
from sqlalchemy import and_, or_, func
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from .items import apply_aat, apply_nlp
from .util import ClickIndeterminate
from ..models import Group, Item, create_sessionmaker


async def generate_groups_impl(config):
    """Generate the basic groups."""
    async with create_sessionmaker(config)() as dbsession:
        item_stmt = select(Item).filter(Item.group_id == None)
        count_stmt = select(func.count(Item.id)).filter(Item.group_id == None)
        count = await dbsession.execute(count_stmt)
        result = await dbsession.execute(item_stmt)
        categories = []
        with click.progressbar(
            result.scalars(), length=count.scalar_one(), label='Generating potential groups'
        ) as progress:
            for item in progress:
                for category in item.attributes['_categories']:
                    categories.append(category.lower())
        counts = [(cat, count) for cat, count in Counter(categories).most_common() if count >= 15]
        counts.sort(key=lambda c: c[1])
        max_groups = len(counts)
        with click.progressbar(length=max_groups, label='Generating groups') as progress:
            while counts:
                category = counts[0][0]
                group_stmt = select(Group).filter(Group.value == category)
                result = await dbsession.execute(group_stmt)
                group = result.scalars().first()
                if group is None:
                    group = Group(value=category, label=category[0].upper() + category[1:], split='basic')
                    dbsession.add(group)
                result = await dbsession.execute(item_stmt)
                for item in result.scalars():
                    if category in item.attributes['_categories']:
                        item.group = group
                await dbsession.commit()
                categories = []
                result = await dbsession.execute(item_stmt)
                for item in result.scalars():
                    for category in item.attributes['_categories']:
                        categories.append(category.lower())
                old_counts = len(counts)
                counts = [(cat, count) for cat, count in Counter(categories).most_common() if count >= 15]
                counts.sort(key=lambda c: c[1])
                progress.update(old_counts - len(counts))
        await dbsession.commit()


@click.command()
@click.pass_context
def generate_groups(ctx):
    """Generate the basic groups."""
    asyncio.run(generate_groups_impl(ctx.obj['config']))


def fill_vector(group):
    """Create a full vector from a sparse vector in the database."""
    vec = array([0 for _ in range(0, 300)], dtype=float)
    for dim, value in group.attributes['lda_vector']:
        vec[dim] = value
    return vec


def split_by_similarity(dbsession, group):
    """Split the groups by similarity."""
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
    new_group = Group(value=group.value, label=group.label, parent=group, split='similar')
    dbsession.add(new_group)
    count = 0
    for item in sorted_items:
        if count > limit:
            new_group = Group(value=group.value, label=group.label, parent=group, split='similar')
            dbsession.add(new_group)
            count = 0
        item.group = new_group
        count = count + 1


def split_by_attribute(dbsession, group, attr):
    """Split the group by the values of a given attribute."""
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
                new_group = Group(
                    value=category[0], label=f'{group.label} - {category[0]}', parent=group, split='attribute'
                )
                dbsession.add(new_group)
                for item in list(group.items):
                    if category[0] in item.attributes[attr]:
                        item.group = new_group
            new_group = Group(value=group.label, label=group.label, parent=group, split='attribute')
            dbsession.add(new_group)
            for item in list(group.items):
                item.group = new_group
            return True
    return False


def split_by_year(config, dbsession, group):
    """Split the group by year."""
    years = []
    decades = []
    centuries = []
    with_year = 0
    for item in group.items:
        if config['data']['year_field'] in item.attributes and item.attributes[config['data']['year_field']]:
            years.append(item.attributes[config['data']['year_field']])
            with_year = with_year + 1
    if with_year / len(group.items) > 0.95:
        common = [(int(v), c) for v, c in Counter(years).most_common()]
        start_year = min([c for c, _ in common])
        end_year = max([c for c, _ in common])
        if start_year != end_year:
            year_boundaries = []
            if (end_year - start_year) <= 100 and (end_year - start_year) > 10:
                start_decade = math.floor(start_year / 10)
                end_decade = math.floor(end_year / 10)
                decades = []
                for start_year in range(start_decade * 10, (end_decade + 1) * 10, 10):
                    for item in list(group.items):
                        if (
                            config['data']['year_field'] in item.attributes
                            and item.attributes[config['data']['year_field']]
                        ):
                            if (
                                start_year <= int(item.attributes[config['data']['year_field']])
                                and int(item.attributes[config['data']['year_field']]) < start_year + 10
                            ):
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
                        if (
                            config['data']['year_field'] in item.attributes
                            and item.attributes[config['data']['year_field']]
                        ):
                            if (
                                years[0] <= int(item.attributes[config['data']['year_field']])
                                and int(item.attributes[config['data']['year_field']]) < years[-1] + 10
                            ):
                                if new_group is None:
                                    if len(years) == 1:
                                        label = f'{years[0]}s'
                                    else:
                                        label = f'{years[0]}s-{years[-1]}s'
                                    new_group = Group(
                                        value=str(start_year),
                                        label=f'{group.label} - {label}',
                                        parent=group,
                                        split='time',
                                    )
                                    dbsession.add(new_group)
                                item.group = new_group
                if group.items:
                    new_group = Group(value=group.label, label=group.label, parent=group, split='time')
                    dbsession.add(new_group)
                    for item in list(group.items):
                        item.group = new_group
                return True
            elif (end_year - start_year) > 100:
                start_century = math.floor(start_year / 100)
                end_century = math.floor(end_year / 100)
                centuries = []
                for start_year in range(start_century * 100, (end_century + 1) * 100, 100):
                    for item in list(group.items):
                        if (
                            config['data']['year_field'] in item.attributes
                            and item.attributes[config['data']['year_field']]
                        ):
                            if (
                                start_year <= int(item.attributes[config['data']['year_field']])
                                and int(item.attributes[config['data']['year_field']]) < start_year + 100
                            ):
                                if len(centuries) == 0 or centuries[-1][0][0] != start_year:
                                    centuries.append([[start_year], 1])
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
                        if (
                            config['data']['year_field'] in item.attributes
                            and item.attributes[config['data']['year_field']]
                        ):
                            if (
                                years[0] <= int(item.attributes[config['data']['year_field']])
                                and int(item.attributes[config['data']['year_field']]) < years[-1] + 100
                            ):
                                if new_group is None:
                                    if len(years) == 1:
                                        century = math.floor(years[0] / 100) + 1
                                        if century % 10 == 1 and century != 11:
                                            label = f'{century}st'
                                        elif century % 10 == 2 and century != 12:
                                            label = f'{century}nd'
                                        elif century % 10 == 3 and century != 13:
                                            label = f'{century}rd'
                                        else:
                                            label = f'{century}th'
                                    else:
                                        century = math.floor(years[0] / 100) + 1
                                        if century % 10 == 1 and century != 11:
                                            start_label = f'{century}st'
                                        elif century % 10 == 2 and century != 12:
                                            start_label = f'{century}nd'
                                        elif century % 10 == 3 and century != 13:
                                            start_label = f'{century}rd'
                                        else:
                                            start_label = f'{century}th'
                                        century = math.floor(years[-1] / 100) + 1
                                        if century % 10 == 1 and century != 11:
                                            end_label = f'{century}st'
                                        elif century % 10 == 2 and century != 12:
                                            end_label = f'{century}nd'
                                        elif century % 10 == 3 and century != 13:
                                            end_label = f'{century}rd'
                                        else:
                                            end_label = f'{century}th'
                                        label = f'{start_label}-{end_label}'
                                    new_group = Group(
                                        value=str(start_year),
                                        label=f'{group.label} - {label} century',
                                        parent=group,
                                        split='time',
                                    )
                                    dbsession.add(new_group)
                                item.group = new_group
                if group.items:
                    new_group = Group(value=group.label, label=group.label, parent=group, split='time')
                    dbsession.add(new_group)
                    for item in list(group.items):
                        item.group = new_group
                return True
    return False


async def split_large_groups_impl(config):
    """Split large groups into smaller ones."""
    async with create_sessionmaker(config)() as dbsession:
        progress = ClickIndeterminate('Splitting large groups')
        progress.start()
        splitting = True
        stmt = select(Group).options(selectinload(Group.items), selectinload(Group.children))
        while splitting:
            splitting = False
            result = await dbsession.execute(stmt)
            for group in result.scalars():
                if len(group.children) == 0:
                    if len(group.items) > 120 and len(group.items) < 300:
                        if split_by_year(config, dbsession, group):
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
                        elif split_by_year(config, dbsession, group):
                            splitting = True
                        else:
                            split_by_similarity(dbsession, group)
                            splitting = True
            await dbsession.commit()
        progress.stop()


@click.command()
@click.pass_context
def split_large_groups(ctx):
    """Split large groups into smaller ones."""
    asyncio.run(split_large_groups_impl(ctx.obj['config']))


async def merge_singular_plural_impl(config):
    """Merge singular and plural groups."""
    async with create_sessionmaker(config)() as dbsession:
        progress = ClickIndeterminate('Merging singular and plural')
        progress.start()
        modifying = True
        while modifying:
            modifying = False
            stmt = select(Group)
            result = await dbsession.execute(stmt)
            for group in result.scalars():
                stmt = (
                    select(Group)
                    .filter(and_(Group.value == inflection.singularize(group.value), Group.id != group.id))
                    .options(selectinload(Group.items))
                )
                result = await dbsession.execute(stmt)
                other = result.scalars().first()
                if other:
                    for item in list(other.items):
                        item.group = group
                        dbsession.add(item)
                    await dbsession.delete(other)
                    await dbsession.commit()
                    modifying = True
                    break
        progress.stop()


@click.command()
@click.pass_context
def merge_singular_plural(ctx):
    """Merge singular and plural groups."""
    asyncio.run(merge_singular_plural_impl(ctx.obj['config']))


async def add_parent_groups_impl(config):
    """Add any required parent groups."""
    async with create_sessionmaker(config)() as dbsession:
        stmt = select(Group).filter(Group.parent_id == None).options(selectinload(Group.parent))
        result = await dbsession.execute(stmt)
        stmt = select(func.count(Group.id)).filter(Group.parent_id == None)
        result_count = await dbsession.execute(stmt)
        with click.progressbar(
            result.scalars(), length=result_count.scalar_one(), label='Adding parent groups'
        ) as progress:
            for group in progress:
                if 'aat' in config['data']['hierarchy']['expansions']:
                    categories = apply_aat(group.value, merge=False)
                    if categories:
                        for category_list in categories:
                            mapped = False
                            for category in category_list:
                                stmt = select(Group).filter(Group.value == category)
                                result = await dbsession.execute(stmt)
                                parent_group = result.scalars().first()
                                if not parent_group:
                                    parent_group = Group(
                                        value=category, label=category[0].upper() + category[1:], split='parent'
                                    )
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
                            stmt = select(Group).filter(
                                or_(Group.value == category, Group.value == inflection.pluralize(category))
                            )
                            result = await dbsession.execute(stmt)
                            parent_group = result.scalars().first()
                            if parent_group:
                                group.parent = parent_group
                                await dbsession.commit()
                                mapped = True
                                break
                        if not mapped:
                            if group.value not in ['styles and periods']:
                                for category in apply_nlp(group.value):
                                    hierarchies = apply_aat(category, merge=False)
                                    groups = []
                                    for hierarchy in hierarchies:
                                        if group.value not in hierarchy:
                                            stmt = (
                                                select(Group)
                                                .filter(Group.value.in_(hierarchy))
                                                .options(selectinload(Group.items))
                                            )
                                            result = await dbsession.execute(stmt)
                                            for potential_group in result.scalars():
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
        await dbsession.commit()


@click.command()
@click.pass_context
def add_parent_groups(ctx):
    """Add any required parent groups."""
    asyncio.run(add_parent_groups_impl(ctx.obj['config']))


async def prune_single_groups_impl(config):
    """Remove groups that have a single child and no items."""
    async with create_sessionmaker(config)() as dbsession:
        progress = ClickIndeterminate('Pruning single groups')
        progress.start()
        pruning = True
        stmt = select(Group).options(selectinload(Group.children), selectinload(Group.items))
        while pruning:
            pruning = False
            result = await dbsession.execute(stmt)
            for group in result.scalars():
                if len(group.items) == 0 and len(group.children) == 1:
                    group.children[0].parent = group.parent
                    await dbsession.delete(group)
                    await dbsession.commit()
                    pruning = True
                    break
        progress.stop()


@click.command()
@click.pass_context
def prune_single_groups(ctx):
    """Remove groups that have a single child and no items."""
    asyncio.run(prune_single_groups_impl(ctx.obj['config']))


async def move_inner_items_impl(config):
    """Move items from non-leaf groups into extra leaf groups."""
    async with create_sessionmaker(config)() as dbsession:
        progress = ClickIndeterminate('Moving inner items')
        progress.start()
        moving = True
        stmt = select(Group).options(selectinload(Group.children), selectinload(Group.items))
        while moving:
            moving = False
            result = await dbsession.execute(stmt)
            for group in result.scalars():
                if len(group.items) > 0 and len(group.children) > 0:
                    sub_group = Group(value=group.value, label=group.label, split='inner')
                    dbsession.add(sub_group)
                    sub_group.parent = group
                    for item in list(group.items):
                        item.group = sub_group
                        dbsession.add(item)
                    await dbsession.commit()
                    moving = True
                    break
        await dbsession.commit()
        progress.stop()


@click.command()
@click.pass_context
def move_inner_items(ctx):
    """Move items from non-leaf groups into extra leaf groups."""
    asyncio.run(move_inner_items_impl(ctx.obj['config']))


async def pipeline_impl(config):
    """Run the group processing pipeline."""
    await generate_groups_impl(config)
    await merge_singular_plural_impl(config)
    await add_parent_groups_impl(config)
    await prune_single_groups_impl(config)
    await move_inner_items_impl(config)
    await split_large_groups_impl(config)


@click.command()
@click.pass_context
def pipeline(ctx):
    """Run the group processing pipeline."""
    asyncio.run(pipeline_impl(ctx.obj['config']))


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
