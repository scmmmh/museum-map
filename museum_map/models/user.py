"""Models for the user."""
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import Column, Index, Integer, Unicode

from museum_map.models.base import Base


class User(Base):
    """Database model representing one user."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)  # noqa: A003
    public_id = Column(Unicode(255), unique=True)


Index(User.public_id)


class UserModel(BaseModel):
    """Pydantic model representing a room."""

    id: str = Field(validation_alias="public_id")  # noqa: A003

    model_config = ConfigDict(from_attributes=True)
