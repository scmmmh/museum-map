from pyramid.httpexceptions import HTTPNotFound
from pyramid.view import view_config

from ..models import Group

@view_config(route_name='explore', renderer='museum_map:templates/interface.kajiki')
def root(request):
    group = request.dbsession.query(Group).filter(Group.id == request.matchdict['gid']).first()
    return {'group': group, 'hierarchy': [Group(id=-1, title='Loading...')]}
