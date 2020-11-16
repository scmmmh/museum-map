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


Index(Item.group_id)
