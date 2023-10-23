"""Database models."""
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from museum_map.models.base import Base  # noqa
from museum_map.models.floor import Floor, FloorTopic  # noqa
from museum_map.models.group import Group  # noqa
from museum_map.models.item import Item  # noqa
from museum_map.models.room import Room  # noqa
from museum_map.settings import settings

async_engine = create_async_engine(settings.db.dsn)
async_sessionmaker = sessionmaker(
    bind=async_engine, expire_on_commit=False, autoflush=False, autocommit=False, class_=AsyncSession
)


async def db_session() -> None:
    dbsession = async_sessionmaker()
    try:
        yield dbsession
    finally:
        await dbsession.close()
