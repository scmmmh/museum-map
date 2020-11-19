from sqlalchemy import (Column, Integer, Unicode, ForeignKey, Index)
from sqlalchemy.orm import relationship
from sqlalchemy_json import NestedMutableJson

from .base import Base


class Room(Base):

    __tablename__ = 'rooms'

    id = Column(Integer, primary_key=True)
    group_id = Column(Integer, ForeignKey('groups.id'))
    number = Column(Unicode(16))

    group = relationship('Group', back_populates='room')


class RoomLink(Base):

    __tablename__ = 'room_links'

    id = Column(Integer, primary_key=True)
    from_id = Column(Integer, ForeignKey('rooms.id'))
    to_id = Column(Integer, ForeignKey('rooms.id'))
    position = Column(Unicode(16))
    order = Column(Integer)
    link = Column(Unicode(16))
