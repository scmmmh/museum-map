from sqlalchemy import (Table, Column, Integer, Unicode, UnicodeText, ForeignKey, Index)
from sqlalchemy.orm import relationship
from sqlalchemy_json import NestedMutableJson

from .base import Base


floors_items = Table('floors_items', Base.metadata,
                     Column('floor_id', Integer, ForeignKey('floors.id')),
                     Column('item_id', Integer, ForeignKey('items.id')))


class Floor(Base):

    __tablename__ = 'floors'

    id = Column(Integer, primary_key=True)
    label = Column(Unicode(255))
    level = Column(Integer)

    rooms = relationship('Room', back_populates='floor')
    samples = relationship('Item', secondary=floors_items)
    topics = relationship('FloorTopic', back_populates='floor')

    def as_jsonapi(self):
        return {
            'type': 'floors',
            'id': str(self.id),
            'attributes': {
                'label': self.label,
                'level': self.level,
            },
            'relationships': {
                'rooms': {
                    'data': [
                        {
                            'type': 'rooms',
                            'id': str(room.id)
                        }
                        for room in self.rooms
                    ]
                },
                'samples': {
                    'data': [
                        {
                            'type': 'items',
                            'id': str(item.id)
                        }
                        for item in self.samples
                    ]
                },
                'topics': {
                    'data': [
                        {
                            'type': 'floor-topics',
                            'id': str(topic.id)
                        }
                        for topic in self.topics
                    ]
                }
            }
        }


class FloorTopic(Base):

    __tablename__ = 'floor_topics'

    id = Column(Integer, primary_key=True)
    floor_id = Column(Integer, ForeignKey('floors.id'))
    room_id = Column(Integer, ForeignKey('rooms.id'))
    label = Column(Unicode(255))

    floor = relationship('Floor', back_populates='topics')
    room = relationship('Room')

    def as_jsonapi(self):
        return {
            'type': 'floor-topics',
            'id': str(self.id),
            'attributes': {
                'label': self.label
            },
            'relationships': {
                'floor': {
                    'data': {
                        'type': 'floors',
                        'id': str(self.floor_id)
                    }
                },
                'room': {
                    'data': {
                        'type': 'rooms',
                        'id': str(self.room_id)
                    }
                }
            }
        }
