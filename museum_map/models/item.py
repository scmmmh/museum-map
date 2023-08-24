from sqlalchemy import Column, Integer, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy_json import NestedMutableJson

from .base import Base


class Item(Base):
    __tablename__ = 'items'

    id = Column(Integer, primary_key=True)
    group_id = Column(Integer, ForeignKey('groups.id'))
    room_id = Column(Integer, ForeignKey('rooms.id'))
    attributes = Column(NestedMutableJson)
    sequence = Column(Integer)

    group = relationship('Group', back_populates='items')
    room = relationship('Room', back_populates='items', primaryjoin='Item.room_id == Room.id')

    def as_jsonapi(self):
        data = {'type': 'items', 'id': str(self.id), 'attributes': self.attributes, 'relationships': {}}
        if self.room:
            data['relationships']['room'] = {'data': {'type': 'rooms', 'id': str(self.room_id)}}
        return data


Index(Item.group_id)
Index(Item.room_id)
