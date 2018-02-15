from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config

from ..models import Group

@view_config(route_name='root')
def root(request):
    raise HTTPFound(location=request.route_url('explore'))
