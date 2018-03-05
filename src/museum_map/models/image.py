from sqlalchemy import (Column, Integer, ForeignKey, String, Boolean, Index)

from .meta import Base


class Image(Base):
    __tablename__ = 'images'

    id = Column(Integer, primary_key=True)
    item_id = Column(Integer, ForeignKey('items.id'))
    path = Column(String)
    size = Column(String)
    width = Column(Integer)
    height = Column(Integer)
    primary = Column(Boolean)

Index('images_item_id_size_ix', Image.item_id, Image.size)
Index('images_item_id_primary_ix', Image.item_id, Image.primary)
Index('images_item_id_primary__sizeix', Image.item_id, Image.primary, Image.size)
