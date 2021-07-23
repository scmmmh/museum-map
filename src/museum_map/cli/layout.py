import click

from copy import deepcopy
from inflection import pluralize
from random import sample, choice
from scipy.spatial.distance import cosine
from sqlalchemy import create_engine, and_, not_
from sqlalchemy.orm import sessionmaker

from .groups import fill_vector
from ..models import Base, Item, Group, Room, Floor, FloorTopic


def count_items(group):
    if len(group.items) > 0:
        return len(group.items)
    else:
        return sum([count_items(child) for child in group.children])


def get_assignable_groups(dbsession, assigned):
    groups = []

    def walk(node):
        if node.id not in assigned and len(node.items) > 0 and not node.room:
            groups.append(node)
        for child in node.children:
            walk(child)

    for root in dbsession.query(Group).filter(Group.parent_id == None):
        walk(root)
    return groups


def pluralize_label(label):
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


def generate_rooms(dbsession, floor, nr, room_ids, rooms, assigned):
    while room_ids:
        rid = room_ids.pop()
        room = rooms[rid]
        splits_left = 1  # room['max_splits']
        items_left = room['max_items']
        for group in get_assignable_groups(dbsession, assigned):
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


def generate_structure_impl(ctx):
    engine = create_engine(ctx.obj['config'].get('db', 'uri'))
    Base.metadata.bind = engine
    dbsession = sessionmaker(bind=engine)()
    room_ids = [rid.strip() for rid in ctx.obj['config'].get('floorplan', 'rooms').split(',')]
    links = {}
    for from_id, to_id in [l.strip().split('.') for l in ctx.obj['config'].get('floorplan', 'links').split(',')]:
        if from_id not in links:
            links[from_id] = [to_id]
        else:
            links[from_id].append(to_id)
    room_ids.reverse()

    def room_settings(rid):
        direction, max_items, max_splits, position  = [v.strip() for v in ctx.obj['config'].get('floorplan', rid).split(',')]
        return {'direction': direction,
                'max_items': int(max_items),
                'max_splits': int(max_splits),
                'position': position,
                'links': links[rid] if rid in links else []}

    rooms = dict([(rid, room_settings(rid)) for rid in room_ids])
    assigned = []
    assignable = get_assignable_groups(dbsession, assigned)
    old_len = len(assignable)
    floor_nr = -1
    progress = click.progressbar(length=len(assignable), label='Generating layout')
    while assignable:
        floor_nr = floor_nr + 1
        floor = Floor(label = f'Floor {floor_nr}', level=floor_nr)
        dbsession.add(floor)
        generate_rooms(dbsession, floor, 1, deepcopy(room_ids), rooms, assigned)
        assignable = get_assignable_groups(dbsession, assigned)
        progress.update(old_len - len(assignable))
        old_len = len(assignable)
    dbsession.commit()


@click.command()
@click.pass_context
def generate_structure(ctx):
    """Generate the floors and rooms structure."""
    generate_structure_impl(ctx)


def get_basic_group(group):
    if group.split == 'basic':
        return group
    else:
        return get_basic_group(group.parent)


def depth(group):
    if group.parent:
        return 1 + depth(group.parent)
    else:
        return 0


def get_ancestors(group):
    if group.parent:
        return [group.parent] + get_ancestors(group.parent)
    else:
        return []


def summarise_floor(dbsession, floor):
    # Generate the sample images
    floor.samples = [choice(room.items) for room in sample(floor.rooms, min(15, len(floor.rooms)))]
    for room in floor.rooms:
        room.sample = choice(room.items)
    # Generate the topic list
    if True or len(floor.topics) == 0:
        floor_groups = {}
        for room in floor.rooms:
            group = room.group
            size = count_items(group)
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


def generate_summaries_impl(ctx):
    engine = create_engine(ctx.obj['config'].get('db', 'uri'))
    Base.metadata.bind = engine
    dbsession = sessionmaker(bind=engine)()
    dbsession.query(FloorTopic).delete()
    query = dbsession.query(Floor)
    with click.progressbar(query, length=query.count(), label='Generating floor summaries') as progress:
        for floor in progress:
            summarise_floor(dbsession, floor)
    dbsession.commit()


@click.command()
@click.pass_context
def generate_summaries(ctx):
    """Generate the floor and room summaries"""
    generate_summaries_impl(ctx)


def order_items_impl(ctx):
    engine = create_engine(ctx.obj['config'].get('db', 'uri'))
    Base.metadata.bind = engine
    dbsession = sessionmaker(bind=engine)()
    query = dbsession.query(Room)
    with click.progressbar(query, length=query.count(), label='Ordering items in rooms') as progress:
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
    dbsession.commit()


@click.command()
@click.pass_context
def order_items(ctx):
    """Order the items in each room"""
    order_items_impl(ctx)


@click.command()
@click.pass_context
def pipeline(ctx):
    generate_structure_impl(ctx)
    generate_summaries_impl(ctx)
    order_items_impl(ctx)


@click.group()
def layout():
    """Layout generation commands."""
    pass


layout.add_command(generate_structure)
layout.add_command(generate_summaries)
layout.add_command(order_items)
layout.add_command(pipeline)
