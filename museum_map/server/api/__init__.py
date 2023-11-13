"""The main REST API."""
import logging
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from museum_map.__about__ import __tables__, __version__
from museum_map.models import db_session
from museum_map.server.api import floor_topics, floors

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api")
router.include_router(floors.router)
router.include_router(floor_topics.router)


@router.get("/")
async def index(dbsession: Annotated[AsyncSession, Depends(db_session)]) -> dict:
    """Return the application status."""
    try:
        logger.debug("API readyness check")
        query = text(
            "SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname != 'pg_catalog' AND schemaname != 'information_schema'"  # noqa: E501
        )
        tables = set((await dbsession.execute(query)).scalars())
        return {"ready": tables == __tables__, "version": __version__}
    except Exception as e:
        logger.error(e)
        return {"ready": False, "version": __version__}
