from sqlalchemy import (Column, Integer, ForeignKey, Index)
from sqlalchemy.orm import relationship
from sqlalchemy_json import NestedMutableJson

from .base import Base


class Item(Base):

    __tablename__ = 'items'

    id = Column(Integer, primary_key=True)
    group_id = Column(Integer, ForeignKey('groups.id'))
    attributes = Column(NestedMutableJson)

    group = relationship('Group', back_populates='items')

    def as_jsonapi(self):
        return {
            'type': 'items',
            'id': str(self.id),
            'attributes': self.attributes,
            'relationships': {
                'group': {
                    'data': {
                        'type': 'groups',
                        'id': str(self.group_id)
                    }
                }
            }
        }


Index(Item.group_id)
