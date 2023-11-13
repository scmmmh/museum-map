"""Data model for the floors and floor-topics."""
from pydantic import BaseModel, ConfigDict, field_validator
from sqlalchemy import Column, ForeignKey, Index, Integer, Table, Unicode
from sqlalchemy.orm import relationship

from museum_map.models.base import Base

floors_items = Table(
    "floors_items",
    Base.metadata,
    Column("floor_id", Integer, ForeignKey("floors.id")),
    Column("item_id", Integer, ForeignKey("items.id")),
)


class Floor(Base):
    """Represents a single floor in the database."""

    __tablename__ = "floors"

    id = Column(Integer, primary_key=True)  # noqa: A003
    label = Column(Unicode(255))
    level = Column(Integer)

    rooms = relationship("Room", back_populates="floor")
    samples = relationship("Item", secondary=floors_items)
    topics = relationship("FloorTopic", back_populates="floor")


class FloorModel(BaseModel):
    """Pydantic model for validating a floor."""

    id: int  # noqa: A003
    label: str
    level: int
    rooms: list[int]
    samples: list[int]
    topics: list[int]

    model_config = ConfigDict(from_attributes=True)

    @field_validator("rooms", "samples", "topics", mode="before")
    @classmethod
    def convert_model_to_ids(cls, value: list[any]) -> str:
        """Convert the lists of child models to lists of ids."""
        return [v.id for v in value]


class FloorTopic(Base):
    """Represents a single floor topic in the database."""

    __tablename__ = "floor_topics"

    id = Column(Integer, primary_key=True)  # noqa: A003
    group_id = Column(Integer, ForeignKey("groups.id"))
    floor_id = Column(Integer, ForeignKey("floors.id"))
    label = Column(Unicode(255))
    size = Column(Integer)

    group = relationship("Group")
    floor = relationship("Floor", back_populates="topics")


Index(FloorTopic.group_id)
Index(FloorTopic.floor_id)


class FloorTopicModel(BaseModel):
    """Pydantic model for validating a floor-topic."""

    id: int  # noqa: A003
    group: int
    floor: int
    label: str
    size: int

    model_config = ConfigDict(from_attributes=True)

    @field_validator("group", "floor", mode="before")
    @classmethod
    def convert_model_to_id(cls, value: any) -> str:
        """Convert the relationship objects to ids."""
        return value.id
