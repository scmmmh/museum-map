from pywebtools.sqlalchemy import MutableDict, JSONUnicodeText
from sqlalchemy import (Column, Index, Integer, String,)
from sqlalchemy.orm import relationship

from .meta import Base


class AttributesMixin(object):

    def __split_attr_key__(self, key):
        if isinstance(key, tuple):
            if hasattr(self, key[0]):
                return getattr(self, key[0]), key[1]
            elif hasattr(self, 'attributes'):
                return getattr(self, 'attributes'), key[1]
            else:
                return None, None
        elif hasattr(self, 'attributes'):
            return getattr(self, 'attributes'), key
        else:
            return None, None

    def __get_attr_parent__(self):
        if hasattr(self, '__parent_attr__') and hasattr(self, self.__parent_attr__):
            return getattr(self, self.__parent_attr__)
        else:
            return None

    def __contains__(self, key):
        return key in self.attributes

    def __getitem__(self, key):
        return self.attributes[key]

    def __setitem__(self, key, value):
        self.attributes[key] = value


class Item(Base, AttributesMixin):
    __tablename__ = 'items'

    id = Column(Integer, primary_key=True)
    attributes = Column(MutableDict.as_mutable(JSONUnicodeText))

    groups = relationship('Group', secondary='groups_items')
