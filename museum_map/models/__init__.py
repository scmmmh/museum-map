"""Database models."""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, AsyncSession
from sqlalchemy.orm import sessionmaker

from typing import Callable

from .base import Base  # noqa
from .item import Item  # noqa
from .group import Group  # noqa
from .room import Room  # noqa
from .floor import Floor, FloorTopic  # noqa


engine = None


def create_engine(config) -> AsyncEngine:
    """Get a new singleton DB engine."""
    global engine
    if engine is None:
        engine = create_async_engine(config['db']['dsn'])
    return engine


async_sessionmaker = None


def create_sessionmaker(config) -> Callable[[], AsyncSession]:
    """Get a new singleton DB session maker."""
    global async_sessionmaker
    if async_sessionmaker is None:
        async_sessionmaker = sessionmaker(create_engine(config), expire_on_commit=False, class_=AsyncSession)
    return async_sessionmaker
