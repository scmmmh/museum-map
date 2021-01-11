from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from tornado import web

from ..models import Floor, Room, Group, Item


class RequestBase(web.RequestHandler):

    def setup_query(self, types):
        query = None
        class_ = None
        if types == 'rooms':
            query = select(Room)
            class_ = Room
        elif types == 'floors':
            query = select(Floor).options(selectinload(Floor.rooms))
            class_ = Floor
        elif types == 'groups':
            query = select(Group).options(selectinload(Group.children))
            class_ = Group
        elif types == 'items':
            query = select(Item)
            class_ = Item
        return (query, class_)


class APICollectionHandler(RequestBase):

    async def get(self, types):
        async with AsyncSession(self.application.settings['engine']) as session:
            query, class_ = self.setup_query(types)
            if query is not None and class_ is not None:
                for key, values in self.request.arguments.items():
                    if key.startswith('filter['):
                        column = key[key.find('[') + 1:key.find(']')]
                        for value in values:
                            split_values = value.decode().split(',')
                            if len(split_values) == 1:
                                query = query.filter(getattr(class_, column) == split_values[0])
                            else:
                                query = query.filter(getattr(class_, column).in_(split_values))
                result = await session.execute(query)
                items = [item.as_jsonapi() for item in result.scalars()]
                self.write({'data': items})
            else:
                self.send_error(status_code=404)


class APIItemHandler(RequestBase):

    async def get(self, types, identifier):
        async with AsyncSession(self.application.settings['engine']) as session:
            query, class_ = self.setup_query(types)
            if query is not None and class_ is not None:
                query = query.filter(getattr(class_, 'id') == identifier)
                item = (await session.execute(query)).scalars().first()
                if item is not None:
                    self.write({'data': item.as_jsonapi()})
                else:
                    self.send_error(status_code=404)
            else:
                self.send_error(status_code=404)
