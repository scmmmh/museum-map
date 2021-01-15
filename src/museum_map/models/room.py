from sqlalchemy import (Column, Integer, Unicode, ForeignKey, Index)
from sqlalchemy.orm import relationship
from sqlalchemy_json import NestedMutableJson

from .base import Base


class Room(Base):

    __tablename__ = 'rooms'

    id = Column(Integer, primary_key=True)
    floor_id = Column(Integer, ForeignKey('floors.id'))
    group_id = Column(Integer, ForeignKey('groups.id'))
    item_id = Column(Integer, ForeignKey('items.id'))
    number = Column(Unicode(16))
    label = Column(Unicode(255))
    position = Column(Unicode(255))

    group = relationship('Group', back_populates='room')
    floor = relationship('Floor', back_populates='rooms')
    sample = relationship('Item', primaryjoin='Room.item_id == Item.id')
    items = relationship('Item',
                         back_populates='room',
                         order_by='Item.sequence',
                         primaryjoin='Room.id == Item.room_id')

    def as_jsonapi(self):
        data = {
            'type': 'rooms',
            'id': str(self.id),
            'attributes': {
                'number': self.number,
                'label': self.label,
                'position': self.position
            },
            'relationships': {
                'floor': {
                    'data': {
                        'type': 'floors',
                        'id': str(self.floor_id)
                    }
                },
                'items': {
                    'data': [
                        {
                            'type': 'items',
                            'id': str(item.id)
                        }
                        for item in self.items
                    ]
                }
            }
        }
        if self.sample:
            data['relationships']['sample'] = {
                'data': {
                    'type': 'items',
                    'id': str(self.sample.id)
                }
            }
        return data


class RoomLink(Base):

    __tablename__ = 'room_links'

    id = Column(Integer, primary_key=True)
    from_id = Column(Integer, ForeignKey('rooms.id'))
    to_id = Column(Integer, ForeignKey('rooms.id'))
    position = Column(Unicode(16))
    order = Column(Integer)
    link = Column(Unicode(16))
