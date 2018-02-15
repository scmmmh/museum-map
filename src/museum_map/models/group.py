from pywebtools.sqlalchemy import MutableDict, JSONUnicodeText
from sqlalchemy import (Column, Index, Integer, String, ForeignKey, Table)
from sqlalchemy.orm import relationship

from .meta import Base

groups_items=Table('groups_items', Base.metadata,
    Column('group_id', Integer, ForeignKey('groups.id'), primary_key=True),
    Column('item_id', Integer, ForeignKey('items.id'), primary_key=True)
)


class Group(Base):
    __tablename__ = 'groups'

    id = Column(Integer, primary_key=True)
    title = Column(String)
    parent_id = Column(Integer, ForeignKey('groups.id'))
    order = Column(Integer)

    parent = relationship('Group', remote_side=[id])
    children = relationship('Group', remote_side=[parent_id], order_by='Group.order')
    items = relationship('Item', secondary=groups_items)

Index('group', groups_items.c.group_id)
