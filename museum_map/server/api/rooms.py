"""Routes for accessing the room data."""
import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from museum_map.models import Room, RoomModel, db_session

router = APIRouter(prefix="/rooms")
logger = logging.getLogger(__name__)


@router.get("/", response_model=list[RoomModel])
async def get_rooms(
    dbsession: Annotated[AsyncSession, Depends(db_session)], rid: Annotated[list[int] | None, Query()] = None
):
    """Retrieve rooms."""
    query = (
        select(Room)
        .options(selectinload(Room.group))
        .options(selectinload(Room.floor))
        .options(selectinload(Room.items))
        .options(selectinload(Room.sample))
    )
    if rid is not None:
        query = query.filter(Room.id.in_(rid))
    return (await dbsession.execute(query)).scalars()
