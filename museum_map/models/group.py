from sqlalchemy import Column, ForeignKey, Index, Integer, Unicode
from sqlalchemy.orm import relationship

from museum_map.models.base import Base


class Group(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True)  # noqa: A003
    parent_id = Column(Integer, ForeignKey("groups.id"))
    value = Column(Unicode(255))
    label = Column(Unicode(255))
    split = Column(Unicode(64))

    parent = relationship("Group", remote_side=[id], back_populates="children", uselist=False)
    children = relationship("Group", remote_side=[parent_id])
    items = relationship("Item", back_populates="group")
    room = relationship("Room", back_populates="group", uselist=False)

    def as_jsonapi(self):
        return {
            "type": "groups",
            "id": str(self.id),
            "attributes": {
                "value": self.value,
                "label": self.label,
                "split": self.split,
            },
        }


Index(Group.parent_id)
