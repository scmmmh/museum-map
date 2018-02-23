import os
import requests

from pyramid.view import view_config
from pyramid.response import Response
from pywebtools.pyramid.util import get_config_setting


@view_config(route_name='image.cache')
def root(request):
    cache_base = get_config_setting(request, 'app.cache_dir')
    cache_path = '%s/%s' % (cache_base, '_'.join(request.matchdict['path']))
    if cache_path and os.path.isfile(cache_path):
        with open(cache_path, 'rb') as in_f:
            data = in_f.read()
    else:
        response = requests.get('http://www.liverpoolmuseums.org.uk/collections2015/images/%s' % '/'.join(request.matchdict['path']))
        data = response.content
        if cache_base:
            with open(cache_path, 'wb') as out_f:
                out_f.write(data)
    return Response(data, content_type='image/jpeg')
