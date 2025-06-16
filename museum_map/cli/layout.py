"""Layout generation CLI commands."""

import asyncio
import math
from copy import deepcopy
from random import choice

import click
from inflection import pluralize
from scipy.spatial.distance import cosine
from sqlalchemy import delete, func
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from museum_map.cli.groups import fill_vector
from museum_map.models import Floor, FloorTopic, Group, Item, Room, async_sessionmaker


async def count_items(dbsession, group):
    """Recursively count the number of items in a group."""
    if len(group.items) > 0:
        return len(group.items)
    else:
        stmt = select(Group).filter(Group.parent_id == group.id).options(selectinload(Group.items))
        result = await dbsession.execute(stmt)
        return sum([count_items(dbsession, child) for child in result.scalars()])


async def get_assignable_groups(dbsession, assigned):
    """Get the groups that are assignable in a more-related-closer-together order."""
    groups = []

    def walk(node):
        if node.id not in assigned and len(node.items) > 0 and not node.room:
            groups.append(node)
        for child in node.children:
            walk(child)

    stmt = select(Group).options(
        selectinload(Group.parent), selectinload(Group.children), selectinload(Group.items), selectinload(Group.room)
    )
    result = await dbsession.execute(stmt)
    for root in result.scalars():
        if root.parent is None:
            walk(root)

    return groups


def pluralize_label(label):
    """Pluralise the label."""
    if " " in label:
        if " - " in label:
            parts = label.split(" - ")
            parts[0] = pluralize_label(parts[0])
            label = " - ".join(parts)
        elif " of " in label:
            part = label[: label.find(" of ")]
            label = f"{pluralize_label(part)}{label[label.find(' of ') :]}"
        elif " for " in label:
            part = label[: label.find(" for ")]
            label = f"{pluralize_label(part)}{label[label.find(' for ') :]}"
        elif " and " in label:
            part1 = label[: label.find(" and ")]
            part2 = label[label.find(" and ") + 5 :]
            label = f"{pluralize_label(part1)} and {pluralize_label(part2)}"
        elif " or " in label:
            part1 = label[: label.find(" or ")]
            part2 = label[label.find(" or ") + 4 :]
            label = f"{pluralize_label(part1)} or {pluralize_label(part2)}"
        else:
            parts = label.split(" ")
            parts[-1] = pluralize(parts[-1])
            label = " ".join(parts)
    else:
        label = pluralize(label)
    return label


async def generate_rooms(dbsession, floor, nr, room_ids, rooms, assigned):
    """Generate the rooms."""
    while room_ids:
        rid = room_ids.pop()
        room = rooms[rid]
        splits_left = 1  # room['max_splits']
        items_left = room["items"]
        for group in await get_assignable_groups(dbsession, assigned):
            if items_left >= len(group.items) and splits_left > 0:
                label = pluralize_label(group.label)
                dbsession.add(
                    Room(
                        number=f"{floor.level}.{nr}",
                        label=label,
                        group=group,
                        floor=floor,
                        items=group.items,
                        position=room["position"],
                    )
                )
                items_left = items_left - len(group.items)
                splits_left = splits_left - 1
                assigned.append(group.id)
                nr = nr + 1
            else:
                break


async def generate_structure_impl(config):
    """Generate the floors and rooms structure."""
    async with async_sessionmaker() as dbsession:
        room_ids = [room["id"] for room in config["layout"]["rooms"]]
        room_ids.reverse()

        rooms = {room["id"]: room for room in config["layout"]["rooms"]}
        assigned = []
        assignable = await get_assignable_groups(dbsession, assigned)
        old_len = len(assignable)
        floor_nr = -1
        progress = click.progressbar(length=len(assignable), label="Generating layout")
        progress.update(0)
        while assignable:
            floor_nr = floor_nr + 1
            floor = Floor(label=f"Floor {floor_nr}", level=floor_nr)
            dbsession.add(floor)
            await generate_rooms(dbsession, floor, 1, deepcopy(room_ids), rooms, assigned)
            assignable = await get_assignable_groups(dbsession, assigned)
            progress.update(old_len - len(assignable))
            old_len = len(assignable)
        await dbsession.commit()


@click.command()
@click.pass_context
def generate_structure(ctx):
    """Generate the floors and rooms structure."""
    asyncio.run(generate_structure_impl(ctx.obj["config"]))


def get_basic_group(group):
    """Find the first basic group."""
    if group.split == "basic":
        return group
    else:
        return get_basic_group(group.parent)


def depth(group):
    """Determine the depth in the hierarchy of a parent."""
    if group.parent:
        return 1 + depth(group.parent)
    else:
        return 0


def get_ancestors(group):
    """Determine all the ancestors of a group."""
    if group.parent:
        return [group.parent, *get_ancestors(group.parent)]
    else:
        return []


async def summarise_rooms(dbsession):
    """Generate the room summaries."""
    rooms = await dbsession.execute(select(Room).options(selectinload(Room.items)))
    rooms_count = await dbsession.execute(select(func.count(Room.id)))
    with click.progressbar(
        rooms.scalars(), length=rooms_count.scalar_one(), label="Generating room summaries"
    ) as progress:
        for room in progress:
            room.sample = choice(room.items)  # noqa: S311
            dbsession.add(room)
    await dbsession.commit()


async def summarise_floors(dbsession):
    """Generate the floor summaries."""
    floors = await dbsession.execute(
        select(Floor).options(selectinload(Floor.topics), selectinload(Floor.rooms), selectinload(Floor.samples))
    )
    floors_count = await dbsession.execute(select(func.count(Floor.id)))
    with click.progressbar(
        floors.scalars(), length=floors_count.scalar_one(), label="Generating floor summaries"
    ) as progress:
        for floor in progress:
            floor_groups = {}
            if len(floor.topics) == 0:
                groups = await dbsession.execute(
                    select(Group).join(Group.room).filter(Room.floor_id == floor.id).options(selectinload(Group.items))
                )
                for group in groups.scalars():
                    size = await count_items(dbsession, group)
                    while group.split in ["time", "similar", "attribute", "inner"]:
                        parent_result = await dbsession.execute(select(Group).filter(Group.id == group.parent_id))
                        group = parent_result.scalar_one()  # noqa: PLW2901
                    if group in floor_groups:
                        floor_groups[group] = floor_groups[group] + size
                    else:
                        floor_groups[group] = size
                group_sizes = list(floor_groups.items())
                group_sizes.sort(key=lambda g: g[1], reverse=True)
                total = sum(floor_groups.values())
                sub_total = 0
                for group, size in group_sizes:
                    sub_total = sub_total + size
                    dbsession.add(FloorTopic(label=pluralize_label(group.label), group=group, floor=floor, size=size))
                    if sub_total / total > 0.66666:  # noqa: PLR2004
                        break
            items_result = await dbsession.execute(
                select(Item).filter(Item.room_id.in_([room.id for room in floor.rooms]))
            )
            items = list(items_result.scalars())
            floor.samples = [items[idx] for idx in range(0, len(items), math.floor(len(items) / 15))]
            await dbsession.commit()


async def generate_summaries_impl():
    """Generate the floor and room summaries."""
    async with async_sessionmaker() as dbsession:
        stmt = delete(FloorTopic)
        await dbsession.execute(stmt)
        await summarise_rooms(dbsession)
        await summarise_floors(dbsession)


@click.command()
def generate_summaries():
    """Generate the floor and room summaries."""
    asyncio.run(generate_summaries_impl())


async def order_items_impl():
    """Order the items by LDA similarity."""
    async with async_sessionmaker() as dbsession:
        stmt = select(Room).options(selectinload(Room.items))
        result = await dbsession.execute(stmt)
        stmt_count = select(func.count(Room.id))
        result_count = await dbsession.execute(stmt_count)
        with click.progressbar(
            result.scalars(), length=result_count.scalar_one(), label="Ordering items in rooms"
        ) as progress:
            for room in progress:
                vectors = {}
                sorted_items = []
                current = room.items[0]
                vectors[current.id] = fill_vector(current)
                while len(sorted_items) < len(room.items):
                    next_item = None
                    next_sim = None
                    for item in room.items:
                        if item in sorted_items:
                            continue
                        if item.id not in vectors:
                            vectors[item.id] = fill_vector(item)
                        if not next_item or cosine(vectors[current.id], vectors[item.id]) > next_sim:
                            next_item = item
                            next_sim = cosine(vectors[current.id], vectors[item.id])
                    if next_item:
                        sorted_items.append(next_item)
                for idx, item in enumerate(sorted_items):
                    item.sequence = idx
                    dbsession.add(item)
        await dbsession.commit()


@click.command()
def order_items():
    """Order the items in each room."""
    asyncio.run(order_items_impl())


async def pipeline_impl():
    """Run the layout pipeline."""
    await generate_structure_impl()
    await generate_summaries_impl()
    await order_items_impl()


@click.command()
def pipeline():
    """Run the layout pipeline."""
    asyncio.run(pipeline_impl())


@click.group()
def layout():
    """Layout generation commands."""
    pass


layout.add_command(generate_structure)
layout.add_command(generate_summaries)
layout.add_command(order_items)
layout.add_command(pipeline)
