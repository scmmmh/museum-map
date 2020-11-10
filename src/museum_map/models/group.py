from sqlalchemy import (Column, Integer, Unicode, ForeignKey)
from sqlalchemy.orm import relationship
from sqlalchemy_json import NestedMutableJson

from .base import Base


class Group(Base):

    __tablename__ = 'groups'

    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('groups.id'))
    value = Column(Unicode(255))
    label = Column(Unicode(255))

    items = relationship('Item', back_populates='group')
