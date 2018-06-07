import json
import transaction

from pyramid.httpexceptions import HTTPBadRequest
from pyramid.view import view_config
from uuid import uuid1

from ..models import Tracking

@view_config(route_name='tracking', renderer='json')
def items(request):
    body = json.loads(request.body.decode('utf-8'))
    if 'action' in body and body['action'] in ['load-url', 'show-item', 'hide-item', 'overview-hover-in', 'overview-hover-out', 'show-note', 'hide-note', 'item-hover-in', 'item-hover-out']:
        if 'uuid' in body:
            uuid = body['uuid']
            del body['uuid']
        else:
            uuid = uuid1().hex
        with transaction.manager:
            request.dbsession.add(Tracking(uuid=uuid, attributes=body))
        return {"uuid": uuid}
    else:
        raise HTTPBadRequest()
