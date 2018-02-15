from pyramid.response import Response
from pyramid.view import view_config
from sqlalchemy.exc import DBAPIError

from ..models import Group

@view_config(route_name='root', renderer='museum_map:templates/interface.kajiki')
def root(request):
    root = request.dbsession.query(Group).filter(Group.parent_id==None).first()
    return {'root': root}
