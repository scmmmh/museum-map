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
