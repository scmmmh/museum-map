import click

from copy import deepcopy
from sqlalchemy import create_engine, and_, not_
from sqlalchemy.orm import sessionmaker

from ..models import Base, Item, Group, Room


def count_items(group):
    if len(group.items) > 0:
        return len(group.items)
    else:
        return sum([count_items(child) for child in group.children if child.split != 'basic'])


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


def generate_rooms(dbsession, floor, nr, room_ids, rooms, assigned):
    while room_ids:
        rid = room_ids.pop()
        room = rooms[rid]
        splits_left = room['max_splits']
        items_left = room['max_items']
        for group in get_assignable_groups(dbsession, assigned):
            if items_left >= len(group.items) and splits_left > 0:
                dbsession.add(Room(number=f'{floor}.{nr}', group=group))
                items_left = items_left - len(group.items)
                splits_left = splits_left - 1
                assigned.append(group.id)
                nr = nr + 1
            else:
                break


@click.command()
@click.pass_context
def generate_layout(ctx):
    """Generate the room layout."""
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
        direction, max_items, max_splits  = [v.strip() for v in ctx.obj['config'].get('floorplan', rid).split(',')]
        return {'direction': direction,
                'max_items': int(max_items),
                'max_splits': int(max_splits),
                'links': links[rid] if rid in links else []}

    rooms = dict([(rid, room_settings(rid)) for rid in room_ids])
    assigned = []
    assignable = get_assignable_groups(dbsession, assigned)
    old_len = len(assignable)
    floor = -1
    progress = click.progressbar(length=len(assignable), label='Generating layout')
    while assignable:
        floor = floor + 1
        generate_rooms(dbsession, floor, 1, deepcopy(room_ids), rooms, assigned)
        assignable = get_assignable_groups(dbsession, assigned)
        progress.update(old_len - len(assignable))
        old_len = len(assignable)
    dbsession.commit()


@click.group()
def rooms():
    """Room generation commands."""
    pass


rooms.add_command(generate_layout)
