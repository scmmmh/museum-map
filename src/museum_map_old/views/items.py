from pyramid.httpexceptions import HTTPNotFound
from pyramid.view import view_config

from ..models import Group

@view_config(route_name='items', renderer='museum_map:templates/items.kajiki')
def items(request):
    group = request.dbsession.query(Group).filter(Group.id == request.matchdict['gid']).first()
    if group is not None:
        return {'group': group}
    else:
        raise HTTPNotFound()
