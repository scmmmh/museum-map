import logging

from fastapi import APIRouter, Depends
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from museum_map.__about__ import __version__, __tables__
from museum_map.models import db_session


router = APIRouter(prefix="/api")
logger = logging.getLogger(__name__)


@router.get("/")
async def index(dbsession: AsyncSession = Depends(db_session)) -> dict():
    """Return the application status."""
    try:
        logger.debug("API readyness check")
        query = text(
            "SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname != 'pg_catalog' AND schemaname != 'information_schema'"
        )
        tables = set((await dbsession.execute(query)).scalars())
        return {"ready": tables == __tables__, "version": __version__}
    except Exception as e:
        logger.error(e)
        return {"ready": False, "version": __version__}
