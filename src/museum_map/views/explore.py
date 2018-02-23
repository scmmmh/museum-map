from pyramid.view import view_config

from ..models import Group

@view_config(route_name='explore', renderer='museum_map:templates/interface.kajiki')
@view_config(route_name='explore.group', renderer='museum_map:templates/interface.kajiki')
def root(request):
    root = request.dbsession.query(Group).filter(Group.parent_id == None).first()
    if 'gid' in request.matchdict:
        current = request.dbsession.query(Group).filter(Group.id == request.matchdict['gid']).first()
    else:
        current = root
    hierarchy = []
    parent = current
    while parent is not None:
        hierarchy.insert(0, parent)
        parent = parent.parent
    return {'root': root, 'current': current, 'hierarchy': hierarchy}
