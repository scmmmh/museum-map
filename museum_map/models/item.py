"""Models for the item."""

from pydantic import BaseModel, ConfigDict, field_validator
from sqlalchemy import Column, ForeignKey, Index, Integer
from sqlalchemy.orm import relationship
from sqlalchemy_json import NestedMutableJson

from museum_map.models.base import Base


class Item(Base):
    """Database model representing a single item."""

    __tablename__ = "items"

    id = Column(Integer, primary_key=True)
    group_id = Column(Integer, ForeignKey("groups.id"))
    room_id = Column(Integer, ForeignKey("rooms.id"))
    attributes = Column(NestedMutableJson)
    sequence = Column(Integer)

    group = relationship("Group", back_populates="items")
    room = relationship("Room", back_populates="items", primaryjoin="Item.room_id == Room.id")


Index(Item.group_id)
Index(Item.room_id)


class ItemModel(BaseModel):
    """Pydantic model for validating items."""

    id: int
    group: int
    room: int
    attributes: dict
    sequence: int

    model_config = ConfigDict(from_attributes=True)

    @field_validator("group", "room", mode="before")
    @classmethod
    def convert_model_to_ids(cls, value: any) -> int:
        """Convert the child models to ids."""
        if value is not None:
            return value.id
        else:
            return None
