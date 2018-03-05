import os
import requests

from pyramid.view import view_config
from pyramid.response import Response, FileResponse
from pywebtools.pyramid.util import get_config_setting

from ..models import Image


@view_config(route_name='image')
def root(request):
    img = request.dbsession.query(Image).filter(Image.id == request.matchdict['iid']).first()
    if img is not None:
        cache_base = get_config_setting(request, 'app.cache_dir')
        cache_path = '%s/%s' % (cache_base, img.id)
        if cache_path and os.path.isfile(cache_path):
            return FileResponse(cache_path, request=request, cache_max_age=2592000)
        response = requests.get('http://www.liverpoolmuseums.org.uk/collections2015/images/%s/v0_%s.jpg' % (img.path.replace('\\', '/'),
                                                                                                            img.size))
        data = response.content
        if cache_base:
            with open(cache_path, 'wb') as out_f:
                out_f.write(data)
        return Response(data, content_type='image/jpeg')
