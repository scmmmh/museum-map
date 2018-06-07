from pywebtools.sqlalchemy import MutableDict, JSONUnicodeText
from sqlalchemy import (Column, Index, Integer, String, DateTime, func)

from .meta import Base
from .mixins import AttributesMixin

class Tracking(Base, AttributesMixin):
    __tablename__ = 'trackings'

    id = Column(Integer, primary_key=True)
    uuid = Column(String)
    timestamp = Column(DateTime, default=func.now())
    attributes = Column(MutableDict.as_mutable(JSONUnicodeText))
