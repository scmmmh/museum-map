"""Models for the rooms."""

from pydantic import BaseModel, ConfigDict, field_validator
from sqlalchemy import Column, ForeignKey, Index, Integer, Unicode
from sqlalchemy.orm import relationship
from sqlalchemy_json import NestedMutableJson

from museum_map.models.base import Base


class Room(Base):
    """Database model representing one room."""

    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True)
    floor_id = Column(Integer, ForeignKey("floors.id"))
    group_id = Column(Integer, ForeignKey("groups.id"))
    item_id = Column(Integer, ForeignKey("items.id"))
    number = Column(Unicode(16))
    label = Column(Unicode(255))
    position = Column(NestedMutableJson)

    group = relationship("Group", back_populates="room")
    floor = relationship("Floor", back_populates="rooms")
    sample = relationship("Item", primaryjoin="Room.item_id == Item.id")
    items = relationship("Item", back_populates="room", order_by="Item.sequence", primaryjoin="Room.id == Item.room_id")


Index(Room.floor_id)
Index(Room.group_id)
Index(Room.item_id)


class RoomModel(BaseModel):
    """Pydantic model representing a room."""

    id: int
    number: str
    label: str
    position: dict
    group: int
    floor: int
    sample: int
    items: list[int]

    model_config = ConfigDict(from_attributes=True)

    @field_validator("items", mode="before")
    @classmethod
    def convert_models_to_ids(cls, value: list[any]) -> str:
        """Convert the lists of child models to lists of ids."""
        return [v.id for v in value]

    @field_validator("group", "floor", "sample", mode="before")
    @classmethod
    def convert_model_to_ids(cls, value: list[any]) -> str:
        """Convert the child models to ids."""
        return value.id
