from sqlalchemy import (Column, Integer, Unicode, ForeignKey, Index)
from sqlalchemy.orm import relationship
from sqlalchemy_json import NestedMutableJson

from .base import Base


class Floor(Base):

    __tablename__ = 'floors'

    id = Column(Integer, primary_key=True)
    label = Column(Unicode(64))
    level = Column(Integer)

    rooms = relationship('Room', back_populates='floor')

    def as_jsonapi(self):
        return {
            'type': 'floors',
            'id': str(self.id),
            'attributes': {
                'label': self.label,
                'level': self.level,
            },
            'relationships': {
                'rooms': [
                    {
                        'type': 'rooms',
                        'id': str(room.id)
                    }
                    for room in self.rooms
                ]
            }
        }
