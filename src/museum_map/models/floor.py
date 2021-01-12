from sqlalchemy import (Column, Integer, Unicode, UnicodeText, ForeignKey, Index)
from sqlalchemy.orm import relationship
from sqlalchemy_json import NestedMutableJson

from .base import Base


class Floor(Base):

    __tablename__ = 'floors'

    id = Column(Integer, primary_key=True)
    label = Column(Unicode(64))
    level = Column(Integer)
    topics = Column(UnicodeText())

    rooms = relationship('Room', back_populates='floor')

    def as_jsonapi(self):
        return {
            'type': 'floors',
            'id': str(self.id),
            'attributes': {
                'label': self.label,
                'level': self.level,
                'topics': self.topics,
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
                }
            }
        }
