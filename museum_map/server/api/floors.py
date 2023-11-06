"""Routes for accessing the floor data."""
import logging
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from museum_map.models import Floor, FloorModel, db_session

router = APIRouter(prefix="/floors")
logger = logging.getLogger(__name__)


@router.get("/", response_model=list[FloorModel])
async def get_floors(dbsession: Annotated[AsyncSession, Depends(db_session)]):
    """Retrieve all floors."""
    query = (
        select(Floor)
        .options(selectinload(Floor.rooms))
        .options(selectinload(Floor.samples))
        .options(selectinload(Floor.topics))
    )
    return (await dbsession.execute(query)).scalars()
