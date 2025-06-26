"""Group generation CLI commands."""

import asyncio
import math
from collections import Counter

import inflection
from numpy import array
from rich.progress import Progress, track
from scipy.spatial.distance import cosine
from sqlalchemy import and_, func, or_
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typer import Typer

from museum_map.cli.items import apply_aat, apply_nlp
from museum_map.models import Group, Item, async_sessionmaker
from museum_map.settings import settings

group = Typer(help="Generate group commands")


async def generate_groups_impl():
    """Generate the basic groups."""
    async with async_sessionmaker() as dbsession:
        item_stmt = select(Item).filter(Item.group_id == None)  # noqa: E711
        count_stmt = select(func.count(Item.id)).filter(Item.group_id == None)  # noqa: E711
        count = await dbsession.execute(count_stmt)
        result = await dbsession.execute(item_stmt)
        categories = []
        for item in track(result.scalars(), total=count.scalar_one(), description="Generating potential groups"):
            for category in item.attributes["_categories"]:
                categories.append(category.lower())
        counts = [(cat, count) for cat, count in Counter(categories).most_common() if count >= 15]  # noqa: PLR2004
        counts.sort(key=lambda c: c[1])
        max_groups = len(counts)
        with Progress() as progress:
            task = progress.add_task("Generating groups", total=max_groups)
            while counts:
                category = counts[0][0]
                group_stmt = select(Group).filter(Group.value == category)
                result = await dbsession.execute(group_stmt)
                group = result.scalars().first()
                if group is None:
                    group = Group(value=category, label=category[0].upper() + category[1:], split="basic")
                    dbsession.add(group)
                result = await dbsession.execute(item_stmt)
                for item in result.scalars():
                    if category in item.attributes["_categories"]:
                        item.group = group
                await dbsession.commit()
                categories = []
                result = await dbsession.execute(item_stmt)
                for item in result.scalars():
                    for category in item.attributes["_categories"]:
                        categories.append(category.lower())
                old_counts = len(counts)
                counts = [
                    (cat, count)
                    for cat, count in Counter(categories).most_common()
                    if count >= 15  # noqa: PLR2004
                ]
                counts.sort(key=lambda c: c[1])
                progress.update(task, advance=old_counts - len(counts))
        await dbsession.commit()


@group.command()
def generate_groups():
    """Generate the basic groups."""
    asyncio.run(generate_groups_impl())


def fill_vector(group):
    """Create a full vector from a sparse vector in the database."""
    return array(group.attributes["lda_vector"])
    # vec = array([0 for _ in range(0, 300)], dtype=float)
    # for dim, value in group.attributes["lda_vector"]:
    #     vec[dim] = value
    # return vec


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
    new_group = Group(value=group.value, label=group.label, parent=group, split="similar")
    dbsession.add(new_group)
    count = 0
    for item in sorted_items:
        if count > limit:
            new_group = Group(value=group.value, label=group.label, parent=group, split="similar")
            dbsession.add(new_group)
            count = 0
        item.group = new_group
        count = count + 1


def split_by_attribute(dbsession, group, attr):
    """Split the group by the values of a given attribute."""
    values = []
    for item in group.items:
        if item.attributes.get(attr):
            values.extend(item.attributes[attr])
    categories = [
        (v, c)
        for v, c in Counter(values).most_common()
        if c < len(group.items) * 0.6666 and c >= 15  # noqa: PLR2004
    ]
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
        if has_values / len(group.items) > 0.9:  # noqa: PLR2004
            categories.reverse()
            for category in categories:
                new_group = Group(
                    value=category[0], label=f"{group.label} - {category[0]}", parent=group, split="attribute"
                )
                dbsession.add(new_group)
                for item in list(group.items):
                    if category[0] in item.attributes[attr]:
                        item.group = new_group
            new_group = Group(value=group.label, label=group.label, parent=group, split="attribute")
            dbsession.add(new_group)
            for item in list(group.items):
                item.group = new_group
            return True
    return False


def split_by_year(dbsession, group):
    """Split the group by year."""
    years = []
    decades = []
    centuries = []
    with_year = 0
    for item in group.items:
        if item.attributes.get(settings.data.year_field):
            years.append(item.attributes[settings.data.year_field])
            with_year = with_year + 1
    if with_year / len(group.items) > 0.95:  # noqa: PLR2004
        common = [(int(v), c) for v, c in Counter(years).most_common()]
        start_year = min([c for c, _ in common])
        end_year = max([c for c, _ in common])
        if start_year != end_year:
            if (end_year - start_year) <= 100 and (end_year - start_year) > 10:  # noqa: PLR2004
                start_decade = math.floor(start_year / 10)
                end_decade = math.floor(end_year / 10)
                decades = []
                for start_year in range(start_decade * 10, (end_decade + 1) * 10, 10):
                    for item in list(group.items):
                        if item.attributes.get(settings.data.year_field):
                            if (
                                start_year <= int(item.attributes[settings.data.year_field])
                                and int(item.attributes[settings.data.year_field]) < start_year + 10
                            ):
                                if len(decades) == 0 or decades[-1][0][0] != start_year:
                                    decades.append([[start_year], 1])
                                else:
                                    decades[-1][1] = decades[-1][1] + 1
                idx = 0
                while idx < len(decades) - 1:
                    if decades[idx][1] + decades[idx + 1][1] < 100:  # noqa: PLR2004
                        decades[idx][0].extend(decades[idx + 1][0])
                        decades[idx][1] = decades[idx][1] + decades[idx + 1][1]
                        decades.pop(idx + 1)
                    else:
                        idx = idx + 1
                for years, _ in decades:
                    new_group = None
                    for item in list(group.items):
                        if item.attributes.get(settings.data.year_field):
                            if (
                                years[0] <= int(item.attributes[settings.data.year_field])
                                and int(item.attributes[settings.data.year_field]) < years[-1] + 10
                            ):
                                if new_group is None:
                                    if len(years) == 1:
                                        label = f"{years[0]}s"
                                    else:
                                        label = f"{years[0]}s-{years[-1]}s"
                                    new_group = Group(
                                        value=str(start_year),
                                        label=f"{group.label} - {label}",
                                        parent=group,
                                        split="time",
                                    )
                                    dbsession.add(new_group)
                                item.group = new_group
                if group.items:
                    new_group = Group(value=group.label, label=group.label, parent=group, split="time")
                    dbsession.add(new_group)
                    for item in list(group.items):
                        item.group = new_group
                return True
            elif (end_year - start_year) > 100:  # noqa: PLR2004
                start_century = math.floor(start_year / 100)
                end_century = math.floor(end_year / 100)
                centuries = []
                for start_year in range(start_century * 100, (end_century + 1) * 100, 100):
                    for item in list(group.items):
                        if item.attributes.get(settings.data.year_field):
                            if (
                                start_year <= int(item.attributes[settings.data.year_field])
                                and int(item.attributes[settings.data.year_field]) < start_year + 100
                            ):
                                if len(centuries) == 0 or centuries[-1][0][0] != start_year:
                                    centuries.append([[start_year], 1])
                                else:
                                    centuries[-1][1] = centuries[-1][1] + 1
                idx = 0
                while idx < len(centuries) - 1:
                    if centuries[idx][1] + centuries[idx + 1][1] < 100:  # noqa: PLR2004
                        centuries[idx][0].extend(centuries[idx + 1][0])
                        centuries[idx][1] = centuries[idx][1] + centuries[idx + 1][1]
                        centuries.pop(idx + 1)
                    else:
                        idx = idx + 1
                for years, _ in centuries:
                    new_group = None
                    for item in list(group.items):
                        if item.attributes.get(settings.data.year_field):
                            if (
                                years[0] <= int(item.attributes[settings.data.year_field])
                                and int(item.attributes[settings.data.year_field]) < years[-1] + 100
                            ):
                                if new_group is None:
                                    if len(years) == 1:
                                        century = math.floor(years[0] / 100) + 1
                                        if century % 10 == 1 and century != 11:  # noqa: PLR2004
                                            label = f"{century}st"
                                        elif century % 10 == 2 and century != 12:  # noqa: PLR2004
                                            label = f"{century}nd"
                                        elif century % 10 == 3 and century != 13:  # noqa: PLR2004
                                            label = f"{century}rd"
                                        else:
                                            label = f"{century}th"
                                    else:
                                        century = math.floor(years[0] / 100) + 1
                                        if century % 10 == 1 and century != 11:  # noqa: PLR2004
                                            start_label = f"{century}st"
                                        elif century % 10 == 2 and century != 12:  # noqa: PLR2004
                                            start_label = f"{century}nd"
                                        elif century % 10 == 3 and century != 13:  # noqa: PLR2004
                                            start_label = f"{century}rd"
                                        else:
                                            start_label = f"{century}th"
                                        century = math.floor(years[-1] / 100) + 1
                                        if century % 10 == 1 and century != 11:  # noqa: PLR2004
                                            end_label = f"{century}st"
                                        elif century % 10 == 2 and century != 12:  # noqa: PLR2004
                                            end_label = f"{century}nd"
                                        elif century % 10 == 3 and century != 13:  # noqa: PLR2004
                                            end_label = f"{century}rd"
                                        else:
                                            end_label = f"{century}th"
                                        label = f"{start_label}-{end_label}"
                                    new_group = Group(
                                        value=str(start_year),
                                        label=f"{group.label} - {label} century",
                                        parent=group,
                                        split="time",
                                    )
                                    dbsession.add(new_group)
                                item.group = new_group
                if group.items:
                    new_group = Group(value=group.label, label=group.label, parent=group, split="time")
                    dbsession.add(new_group)
                    for item in list(group.items):
                        item.group = new_group
                return True
    return False


async def split_large_groups_impl():
    """Split large groups into smaller ones."""
    with Progress() as progress:
        task = progress.add_task("Splitting large groups", total=None)
        async with async_sessionmaker() as dbsession:
            splitting = True
            stmt = select(Group).options(selectinload(Group.items), selectinload(Group.children))
            while splitting:
                splitting = False
                result = await dbsession.execute(stmt)
                for group in result.scalars():
                    if len(group.children) == 0:
                        if len(group.items) > 120 and len(group.items) < 300:  # noqa: PLR2004
                            if split_by_year(dbsession, group):
                                splitting = True
                            else:
                                split_by_similarity(dbsession, group)
                                splitting = True
                        elif len(group.items) >= 300:  # noqa: PLR2004
                            if split_by_attribute(dbsession, group, "concepts"):
                                splitting = True
                            elif split_by_attribute(dbsession, group, "subjects"):
                                splitting = True
                            elif split_by_attribute(dbsession, group, "materials"):
                                splitting = True
                            elif split_by_attribute(dbsession, group, "techniques"):
                                splitting = True
                            elif split_by_year(dbsession, group):
                                splitting = True
                            else:
                                split_by_similarity(dbsession, group)
                                splitting = True
                await dbsession.commit()
        progress.update(task, total=1, completed=1)


@group.command()
def split_large_groups():
    """Split large groups into smaller ones."""
    asyncio.run(split_large_groups_impl())


async def merge_singular_plural_impl():
    """Merge singular and plural groups."""
    with Progress() as progress:
        task = progress.add_task("Merging singular and plural", total=None)
        async with async_sessionmaker() as dbsession:
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
        progress.update(task, total=1, completed=1)


@group.command()
def merge_singular_plural():
    """Merge singular and plural groups."""
    asyncio.run(merge_singular_plural_impl())


async def add_parent_groups_impl():
    """Add any required parent groups."""
    async with async_sessionmaker() as dbsession:
        stmt = select(Group).filter(Group.parent_id == None).options(selectinload(Group.parent))  # noqa: E711
        result = await dbsession.execute(stmt)
        stmt = select(func.count(Group.id)).filter(Group.parent_id == None)  # noqa: E711
        result_count = await dbsession.execute(stmt)
        for group in track(result.scalars(), total=result_count.scalar_one(), description="Adding parent groups"):
            if "aat" in settings.data.hierarchy.expansions:
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
                                    value=category, label=category[0].upper() + category[1:], split="parent"
                                )
                                dbsession.add(group)
                            group.parent = parent_group
                            mapped = True
                            group = parent_group  # noqa: PLW2901
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
                        if group.value not in ["styles and periods"]:
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


@group.command()
def add_parent_groups():
    """Add any required parent groups."""
    asyncio.run(add_parent_groups_impl())


async def prune_single_groups_impl():
    """Remove groups that have a single child and no items."""
    with Progress() as progress:
        task = progress.add_task("Pruning single groups", total=None)
        async with async_sessionmaker() as dbsession:
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
        progress.update(task, total=1, completed=1)


@group.command()
def prune_single_groups():
    """Remove groups that have a single child and no items."""
    asyncio.run(prune_single_groups_impl())


async def move_inner_items_impl():
    """Move items from non-leaf groups into extra leaf groups."""
    with Progress() as progress:
        task = progress.add_task("Moving inner items", total=None)
        async with async_sessionmaker() as dbsession:
            moving = True
            stmt = select(Group).options(selectinload(Group.children), selectinload(Group.items))
            while moving:
                moving = False
                result = await dbsession.execute(stmt)
                for group in result.scalars():
                    if len(group.items) > 0 and len(group.children) > 0:
                        sub_group = Group(value=group.value, label=group.label, split="inner")
                        dbsession.add(sub_group)
                        sub_group.parent = group
                        for item in list(group.items):
                            item.group = sub_group
                            dbsession.add(item)
                        await dbsession.commit()
                        moving = True
                        break
            await dbsession.commit()
        progress.update(task, total=1, completed=1)


@group.command()
def move_inner_items():
    """Move items from non-leaf groups into extra leaf groups."""
    asyncio.run(move_inner_items_impl())


async def pipeline_impl():
    """Run the group processing pipeline."""
    await generate_groups_impl()
    await merge_singular_plural_impl()
    await add_parent_groups_impl()
    await prune_single_groups_impl()
    await move_inner_items_impl()
    await split_large_groups_impl()


@group.command()
def pipeline():
    """Run the group processing pipeline."""
    asyncio.run(pipeline_impl())
