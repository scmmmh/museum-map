from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config

from ..models import Group

@view_config(route_name='root')
def root(request):
    group = request.dbsession.query(Group).filter(Group.parent_id == None).first()
    raise HTTPFound(location=request.route_url('explore', gid=group.id))
