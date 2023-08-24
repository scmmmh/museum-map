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
    __tablename__ = "floors"

    id = Column(Integer, primary_key=True)  # noqa: A003
    label = Column(Unicode(255))
    level = Column(Integer)

    rooms = relationship("Room", back_populates="floor")
    samples = relationship("Item", secondary=floors_items)
    topics = relationship("FloorTopic", back_populates="floor")

    def as_jsonapi(self):
        return {
            "type": "floors",
            "id": str(self.id),
            "attributes": {
                "label": self.label,
                "level": self.level,
            },
            "relationships": {
                "rooms": {"data": [{"type": "rooms", "id": str(room.id)} for room in self.rooms]},
                "samples": {"data": [{"type": "items", "id": str(item.id)} for item in self.samples]},
                "topics": {"data": [{"type": "floor-topics", "id": str(topic.id)} for topic in self.topics]},
            },
        }


class FloorTopic(Base):
    __tablename__ = "floor_topics"

    id = Column(Integer, primary_key=True)  # noqa: A003
    group_id = Column(Integer, ForeignKey("groups.id"))
    floor_id = Column(Integer, ForeignKey("floors.id"))
    label = Column(Unicode(255))
    size = Column(Integer)

    group = relationship("Group")
    floor = relationship("Floor", back_populates="topics")

    def as_jsonapi(self):
        return {
            "type": "floor-topics",
            "id": str(self.id),
            "attributes": {
                "label": self.label,
                "size": self.size,
            },
            "relationships": {
                "group": {"data": {"type": "groups", "id": str(self.group_id)}},
                "floor": {"data": {"type": "floors", "id": str(self.floor_id)}},
            },
        }


Index(FloorTopic.group_id)
Index(FloorTopic.floor_id)
