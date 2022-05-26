import asyncio
import click

from copy import deepcopy
from inflection import pluralize
from random import sample, choice
from scipy.spatial.distance import cosine
from sqlalchemy import func, delete
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from .groups import fill_vector
from ..models import Base, Group, Room, Floor, FloorTopic, create_sessionmaker


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

    stmt = select(Group).options(selectinload(Group.parent), selectinload(Group.children), selectinload(Group.items), selectinload(Group.room))
    result = await dbsession.execute(stmt)
    for root in result.scalars():
        if root.parent is None:
            walk(root)

    return groups


def pluralize_label(label):
    """Pluralise the label."""
    if ' ' in label:
        if ' - ' in label:
            parts = label.split(' - ')
            parts[0] = pluralize_label(parts[0])
            label = ' - '.join(parts)
        elif ' of ' in label:
            part = label[:label.find(' of ')]
            label = f'{pluralize_label(part)}{label[label.find(" of "):]}'
        elif ' for ' in label:
            part = label[:label.find(' for ')]
            label = f'{pluralize_label(part)}{label[label.find(" for "):]}'
        elif ' and ' in label:
            part1 = label[:label.find(' and ')]
            part2 = label[label.find(' and ') + 5:]
            label = f'{pluralize_label(part1)} and {pluralize_label(part2)}'
        elif ' or ' in label:
            part1 = label[:label.find(' or ')]
            part2 = label[label.find(' or ') + 4:]
            label = f'{pluralize_label(part1)} or {pluralize_label(part2)}'
        else:
            parts = label.split(' ')
            parts[-1] = pluralize(parts[-1])
            label = ' '.join(parts)
    else:
        label = pluralize(label)
    return label


async def generate_rooms(dbsession, floor, nr, room_ids, rooms, assigned):
    """Generate the rooms"""
    while room_ids:
        rid = room_ids.pop()
        room = rooms[rid]
        splits_left = 1  # room['max_splits']
        items_left = room['items']
        for group in await get_assignable_groups(dbsession, assigned):
            if items_left >= len(group.items) and splits_left > 0:
                label = pluralize_label(group.label)
                dbsession.add(Room(number=f'{floor.level}.{nr}',
                                   label=label,
                                   group=group,
                                   floor=floor,
                                   items=group.items,
                                   position=room['position']))
                items_left = items_left - len(group.items)
                splits_left = splits_left - 1
                assigned.append(group.id)
                nr = nr + 1
            else:
                break


async def generate_structure_impl(config):
    """Generate the floors and rooms structure."""
    async with create_sessionmaker(config)() as dbsession:
        room_ids = [room['id'] for room in config['layout']['rooms']]
        room_ids.reverse()

        rooms = dict([(room['id'], room) for room in config['layout']['rooms']])
        assigned = []
        assignable = await get_assignable_groups(dbsession, assigned)
        old_len = len(assignable)
        floor_nr = -1
        progress = click.progressbar(length=len(assignable), label='Generating layout')
        progress.update(0)
        while assignable:
            floor_nr = floor_nr + 1
            floor = Floor(label = f'Floor {floor_nr}', level=floor_nr)
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
    asyncio.run(generate_structure_impl(ctx.obj['config']))


def get_basic_group(group):
    """Find the first basic group"""
    if group.split == 'basic':
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
        return [group.parent] + get_ancestors(group.parent)
    else:
        return []


async def summarise_floor(dbsession, floor):
    """Generate a summary for a floor."""
    # Generate the sample images
    stmt = select(Room).filter(Room.id.in_([room.id for room in sample(floor.rooms, min(15, len(floor.rooms)))])).options(selectinload(Room.items), selectinload(Room.sample))
    result = await dbsession.execute(stmt)
    floor.samples = [choice(room.items) for room in result.scalars()]
    rooms_stmt = select(Room).filter(Room.id == floor.id).options(selectinload(Room.items), selectinload(Room.sample), selectinload(Room.group))
    result = await dbsession.execute(rooms_stmt)
    for room in result.scalars():
        room.sample = choice(room.items)
    # Generate the topic list
    if True or len(floor.topics) == 0:
        floor_groups = {}
        result = await dbsession.execute(rooms_stmt)
        for room in result.scalars():
            stmt = select(Group).filter(Group.id == room.group_id).options(selectinload(Group.items), selectinload(Group.parent))
            result = await dbsession.execute(stmt)
            group = result.scalar_one()
            size = await count_items(dbsession, group)
            while group.split in ['time', 'similar', 'attribute', 'inner']:
                group = group.parent
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
            if sub_total / total > 0.66666:
                break
        """groups = set()
        group_rooms = {}
        for room in floor.rooms:
            groups.add(get_basic_group(room.group))
            if room.group not in group_rooms:
                group_rooms[get_basic_group(room.group)] = room
        if len(groups) <= 5:
            for group in groups:
                dbsession.add(FloorTopic(label=pluralize_label(group.label), floor=floor, room=group_rooms[group]))
        else:
            for group in list(groups):
                if group.parent and depth(group.parent) > 3:
                    groups.add(group.parent)
                    group_rooms[group.parent] = group_rooms[group]
            group_sizes = [(group, count_items(group)) for group in groups]
            group_sizes.sort(key=lambda i: i[1])
            added = set()
            count = 0
            while count < 5 and len(group_sizes) > 0:
                group, _ = group_sizes.pop()
                if len(added.intersection(set([group] + get_ancestors(group)))) == 0:
                    dbsession.add(FloorTopic(label=pluralize_label(group.label), floor=floor, room=group_rooms[group]))
                    added.add(group)
                    count = count + 1"""


async def generate_summaries_impl(config):
    """Generate the floor and room summaries"""
    async with create_sessionmaker(config)() as dbsession:
        stmt = delete(FloorTopic)
        await dbsession.execute(stmt)
        stmt = select(Floor).options(selectinload(Floor.rooms), selectinload(Floor.topics), selectinload(Floor.samples))
        result = await dbsession.execute(stmt)
        result_count = await dbsession.execute(select(func.count(Floor.id)))
        with click.progressbar(result.scalars(), length=result_count.scalar_one(), label='Generating floor summaries') as progress:
            for floor in progress:
                await summarise_floor(dbsession, floor)
    await dbsession.commit()


@click.command()
@click.pass_context
def generate_summaries(ctx):
    """Generate the floor and room summaries"""
    asyncio.run(generate_summaries_impl(ctx.obj['config']))


async def order_items_impl(config):
    async with create_sessionmaker(config)() as dbsession:
        stmt = select(Room).options(selectinload(Room.items))
        result = await dbsession.execute(stmt)
        stmt_count = select(func.count(Room.id))
        result_count = await dbsession.execute(stmt_count)
        with click.progressbar(result.scalars(), length=result_count.scalar_one(), label='Ordering items in rooms') as progress:
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
@click.pass_context
def order_items(ctx):
    """Order the items in each room"""
    asyncio.run(order_items_impl(ctx.obj['config']))


async def pipeline_impl(config):
    """Run the layout pipeline."""
    await generate_structure_impl(config)
    await generate_summaries_impl(config)
    await order_items_impl(config)


@click.command()
@click.pass_context
def pipeline(ctx):
    """Run the layout pipeline."""
    asyncio.run(pipeline_impl(ctx.obj['config']))


@click.group()
def layout():
    """Layout generation commands."""
    pass


layout.add_command(generate_structure)
layout.add_command(generate_summaries)
layout.add_command(order_items)
layout.add_command(pipeline)
