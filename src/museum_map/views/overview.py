import math

from pyramid.httpexceptions import HTTPNotFound
from pyramid.view import view_config

from ..models import Group

def split_space(items, bbox, corridor_width=2, allow_children=True):
    rooms = []
    bboxes = []
    direction = 'h'
    while len(items) > 0:
        head = items[0]
        head_size = len(head.items)
        tail = items[1:]
        tail_size = sum([len(t.items) for t in tail])
        split_point = max(0.25, head_size / (head_size + tail_size))
        direction = 'h' if bbox['width'] >= bbox['height'] else 'v'
        if direction == 'h':
            room_bbox = {'top': bbox['top'],
                         'left': bbox['left'],
                         'width': bbox['width'] * split_point - (corridor_width if len(tail) > 0 else 0),
                         'height': bbox['height']}
        else:
            room_bbox = {'top': bbox['top'],
                         'left': bbox['left'],
                         'width': bbox['width'],
                         'height': bbox['height'] * split_point - (corridor_width if len(tail) > 0 else 0)}
        if not allow_children or len(head.children) == 0:
            rooms.append(head)
            bboxes.append(room_bbox)
        elif len(head.children) > 0:
            sub_rooms, sub_bboxes = split_space(list(head.children), room_bbox, corridor_width=corridor_width, allow_children=False)
            rooms.extend(sub_rooms)
            bboxes.extend(sub_bboxes)
        if direction == 'h':
            bbox['left'] = bbox['left'] + bbox['width'] * split_point
            bbox['width'] = bbox['width'] - bbox['width'] * split_point
        else:
            bbox['top'] = bbox['top'] + bbox['height'] * split_point
            bbox['height'] = bbox['height'] - bbox['height'] * split_point
        direction = 'v' if direction == 'h' else 'h'
        items = tail
    return rooms, bboxes


@view_config(route_name='overview', renderer='museum_map:templates/overview.kajiki')
def overview(request):
    root = request.dbsession.query(Group).filter(Group.parent_id == None).first()
    if root is not None:
        try:
            width = int(request.params['width'])
        except Exception:
            try:
                width = math.floor(float(request.params['width']))
            except Exception:
                width = 200
        height = math.ceil(width * (1 / ((1 + math.sqrt(5))/ 2)))
        corridor_width = math.ceil(width / 100)
        floors = []
        for floor in root.children:
            bbox = {'top': 0, 'left': 0, 'width': width, 'height': height}
            rooms, bboxes = split_space(list(floor.children), bbox, corridor_width=corridor_width)
            floors.append({'floor': floor, 'items': zip(rooms, bboxes)})
        return {'floors': floors, 'height': height, 'width': width}
    else:
        raise HTTPNotFound()
