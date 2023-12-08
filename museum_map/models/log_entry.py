"""Models for the user."""
from sqlalchemy import Column, Float, ForeignKey, Index, Integer, Unicode
from sqlalchemy_json import NestedMutableJson

from museum_map.models.base import Base


class LogEntry(Base):
    """Database model representing one log entry."""

    __tablename__ = "log_entries"

    id = Column(Integer, primary_key=True)  # noqa: A003
    user_id = Column(ForeignKey("users.id"))
    action = Column(Unicode(255))
    timestamp = Column(Float)
    params = Column(NestedMutableJson)


Index(LogEntry.user_id)
