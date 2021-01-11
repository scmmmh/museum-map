from sqlalchemy import (Column, Integer, Unicode, ForeignKey, Index)
from sqlalchemy.orm import relationship
from sqlalchemy_json import NestedMutableJson

from .base import Base


class Room(Base):

    __tablename__ = 'rooms'

    id = Column(Integer, primary_key=True)
    floor_id = Column(Integer, ForeignKey('floors.id'))
    group_id = Column(Integer, ForeignKey('groups.id'))
    number = Column(Unicode(16))

    group = relationship('Group', back_populates='room')
    floor = relationship('Floor', back_populates='rooms')

    def as_jsonapi(self):
        return {
            'type': 'rooms',
            'id': str(self.id),
            'attributes': {
                'number': self.number,
            },
            'relationships': {
                'floor': {
                    'data': {
                        'type': 'floors',
                        'id': str(self.floor_id)
                    }
                },
                'group': {
                    'data': {
                        'type': 'groups',
                        'id': str(self.group_id)
                    }
                }
            }
        }


class RoomLink(Base):

    __tablename__ = 'room_links'

    id = Column(Integer, primary_key=True)
    from_id = Column(Integer, ForeignKey('rooms.id'))
    to_id = Column(Integer, ForeignKey('rooms.id'))
    position = Column(Unicode(16))
    order = Column(Integer)
    link = Column(Unicode(16))
