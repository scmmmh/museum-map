from pyramid.httpexceptions import HTTPNotFound
from pyramid.view import view_config

from ..models import Group

@view_config(route_name='breadcrumbs', renderer='museum_map:templates/breadcrumbs.kajiki')
def root(request):
    group = request.dbsession.query(Group).filter(Group.id == request.matchdict['gid']).first()
    hierarchy = []
    parent = group
    while parent is not None:
        hierarchy.insert(0, parent)
        parent = parent.parent
    return {'group': group, 'hierarchy': hierarchy}
