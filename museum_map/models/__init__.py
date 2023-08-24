"""Database models."""
from collections.abc import Callable

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from .base import Base  # noqa
from .floor import Floor, FloorTopic  # noqa
from .group import Group  # noqa
from .item import Item  # noqa
from .room import Room  # noqa

engine = None


def create_engine(config) -> AsyncEngine:
    """Get a new singleton DB engine."""
    global engine
    if engine is None:
        engine = create_async_engine(config["db"]["dsn"])
    return engine


async_sessionmaker = None


def create_sessionmaker(config) -> Callable[[], AsyncSession]:
    """Get a new singleton DB session maker."""
    global async_sessionmaker
    if async_sessionmaker is None:
        async_sessionmaker = sessionmaker(create_engine(config), expire_on_commit=False, class_=AsyncSession)
    return async_sessionmaker
