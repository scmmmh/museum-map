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
    room = relationship('Room', back_populates='group')


Index(Group.parent_id)
