from sqlalchemy import (Column, Integer, Unicode, ForeignKey, Index)
from sqlalchemy.orm import relationship
from sqlalchemy_json import NestedMutableJson

from .base import Base


class Group(Base):

    __tablename__ = 'groups'

    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('groups.id'))
    value = Column(Unicode(255))
    label = Column(Unicode(255))
    split = Column(Unicode(64))

    parent = relationship('Group', remote_side=[id], back_populates='children', uselist=False)
    children = relationship('Group', remote_side=[parent_id])
    items = relationship('Item', back_populates='group')
    room = relationship('Room', back_populates='group', uselist=False)

    def as_jsonapi(self):
        data = {
            'type': 'groups',
            'id': str(self.id),
            'attributes': {
                'value': self.value,
                'label': self.label,
                'split': self.split,
            },
            'relationships': {
                'children': {
                    'data': [
                        {
                            'type': 'groups',
                            'id': str(child.id)
                        }
                        for child in self.children
                    ]
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
        if self.parent:
            data['relationships']['parent'] = {
                'data': {
                    'type': 'groups',
                    'id': str(self.parent_id)
                }
            }
        if self.room:
            data['relationships']['room'] = {
                'data': {
                    'type': 'rooms',
                    'id': str(self.room.id)
                }
            }

        return data


Index(Group.parent_id)
