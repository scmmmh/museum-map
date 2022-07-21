import math

from configparser import ConfigParser
from datetime import datetime
from importlib import resources
from importlib.abc import Traversable
from mimetypes import guess_type
from random import randint
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload, noload
from sqlalchemy.ext.asyncio import AsyncSession
from tornado import web

from ..models import create_sessionmaker, Floor, FloorTopic, Room, Group, Item


class RequestBase(web.RequestHandler):

    def setup_query(self, types):
        query = None
        class_ = None
        if self.get_argument('relationships', 'true').lower() == 'false':
            multi_loader = noload
        else:
            multi_loader = selectinload
        if types == 'rooms':
            query = select(Room).options(selectinload(Room.floor), multi_loader(Room.items), selectinload(Room.sample))
            class_ = Room
        elif types == 'floors':
            query = select(Floor).options(multi_loader(Floor.rooms), multi_loader(Floor.samples), multi_loader(Floor.topics))
            class_ = Floor
        elif types == 'items':
            query = select(Item).options(selectinload(Item.room))
            class_ = Item
        elif types == 'floor-topics':
            query = select(FloorTopic).options(selectinload(FloorTopic.group), selectinload(FloorTopic.floor))
            class_ = FloorTopic
        elif types == 'groups':
            query = select(Group)
            class_ = Group
        return (query, class_)


class APICollectionHandler(RequestBase):

    async def get(self, types):
        async with create_sessionmaker(self.application.settings['config'])() as session:
            query, class_ = self.setup_query(types)
            if query is not None and class_ is not None:
                for key, values in self.request.arguments.items():
                    if key.startswith('filter['):
                        column = key[key.find('[') + 1:key.find(']')]
                        if values == '':
                            query = query.filter(getattr(class_, column).in_([]))
                        else:
                            for value in values:
                                value = value.decode()
                                if value == '':
                                    query = query.filter(getattr(class_, column).in_([]))
                                else:
                                    split_values = [int(v) for v in value.split(',')]
                                    if len(split_values) == 1:
                                        query = query.filter(getattr(class_, column) == split_values[0])
                                    else:
                                        query = query.filter(getattr(class_, column).in_(split_values))
                result = await session.execute(query)
                items = [item.as_jsonapi() for item in result.unique().scalars()]
                self.write({'data': items})
            else:
                self.send_error(status_code=404)


class APIItemHandler(RequestBase):

    async def get(self, types, identifier):
        async with create_sessionmaker(self.application.settings['config'])() as session:
            query, class_ = self.setup_query(types)
            if query is not None and class_ is not None:
                query = query.filter(getattr(class_, 'id') == int(identifier))
                item = (await session.execute(query)).scalars().first()
                if item is not None:
                    self.write({'data': item.as_jsonapi()})
                else:
                    self.send_error(status_code=404)
            else:
                self.send_error(status_code=404)


class APIConfigHandler(web.RequestHandler):

    def initialize(self, config: dict) -> None:
        self._config = config

    async def get(self):
        attributes = {
            'intro': self._config['app']['intro'],
            'item': self._config['app']['item'],
        }
        if 'footer' in self._config['app']:
            for footer_location in ['center', 'right']:
                if footer_location in self._config['app']['footer']:
                    if 'footer' not in attributes:
                        attributes['footer'] = {}
                    attributes['footer'][footer_location] = {
                        'label': self._config['app']['footer'][footer_location]['label']
                    }
                    if 'url' in self._config['app']['footer'][footer_location]:
                        attributes['footer'][footer_location]['url'] = self._config['app']['footer'][footer_location]['url']
        self.write({
            'data': {
                'id': 'all',
                'type': 'configs',
                'attributes': attributes
            }
        })


class APIPickHandler(RequestBase):

    async def get(self, type):
        if type in ['random', 'todays']:
            async with create_sessionmaker(self.application.settings['config'])() as session:
                query, class_ = self.setup_query('items')
                if query is not None and class_ is not None:
                    if type == 'random':
                        query = query.order_by(func.random()).limit(12)
                    elif type == 'todays':
                        total = (await session.execute(select(func.count()).select_from(class_))).scalars().first()
                        row_nr = (math.floor(datetime.utcnow().timestamp() / 86400) % total) + 1
                        query = query.order_by(getattr(class_, 'id')).offset(row_nr).limit(1)
                    result = await session.execute(query)
                    items = [item.as_jsonapi() for item in result.scalars()]
                    self.write({'data': items})
                else:
                    self.send_error(status_code=404)
        else:
            self.send_error(status_code=404)


class FrontendHandler(web.RequestHandler):
    """Handler for the frontend application files."""

    def get(self: 'FrontendHandler', path: str) -> None:
        """Get the file at the given path.

        :param path: The path to get.
        :type: path: str
        """
        self.xsrf_token
        if not path.strip():
            path = '/'
        base = resources.files('museum_map')
        public = base / 'server' / 'frontend' / 'public'
        try:
            self._get_resource(public, path.split('/'))
        except FileNotFoundError:
            self._get_resource(public, ('index.html', ))

    def _get_resource(self: 'FrontendHandler', resource: Traversable, path: list[str]) -> None:
        """Send a file.

        Performs mimetype guessing and sets the appropriate Content-Type header.

        :param resource: The root resource to serve files from
        :type resource: importlib.Traversable
        :param path: The path to the file to send
        :type path: list[str]
        """
        for part in path:
            resource = resource / part
        try:
            data = resource.read_bytes()
            mimetype = guess_type(path[-1])
            if mimetype and mimetype[0]:
                self.set_header('Content-Type', mimetype[0])
            self.write(data)
        except IsADirectoryError:
            raise FileNotFoundError()
