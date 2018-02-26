from pyramid.view import notfound_view_config

from ..models import Group

@notfound_view_config(renderer='museum_map:templates/404.kajiki')
def notfound_view(request):
    root = request.dbsession.query(Group).filter(Group.parent_id == None).first()
    request.response.status = 404
    return {'hierarchy': [root, Group(id=-1, title='The grave-robbers beat you to it')]}
