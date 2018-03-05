from pywebtools.sqlalchemy import MutableDict, JSONUnicodeText
from sqlalchemy import (Column, Index, Integer, String,)
from sqlalchemy.orm import relationship

from .meta import Base
from .mixins import AttributesMixin


class Item(Base, AttributesMixin):
    __tablename__ = 'items'

    id = Column(Integer, primary_key=True)
    attributes = Column(MutableDict.as_mutable(JSONUnicodeText))

    groups = relationship('Group', secondary='groups_items')
    images = relationship('Image')
    primary_medium_img = relationship('Image', uselist=False, primaryjoin='and_(Item.id==Image.item_id, Image.primary==True, Image.size=="medium")')
    primary_large_img = relationship('Image', uselist=False, primaryjoin='and_(Item.id==Image.item_id, Image.primary==True, Image.size=="large")')
