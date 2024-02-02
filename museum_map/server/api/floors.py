"""Routes for accessing the floor data."""
import logging
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from museum_map.models import Floor, FloorModel, Room, RoomModel, db_session

router = APIRouter(prefix="/floors")
logger = logging.getLogger(__name__)


@router.get("/", response_model=list[FloorModel])
async def get_floors(dbsession: Annotated[AsyncSession, Depends(db_session)]):
    """Retrieve all floors."""
    query = (
        select(Floor)
        .order_by(Floor.level)
        .options(selectinload(Floor.rooms))
        .options(selectinload(Floor.samples))
        .options(selectinload(Floor.topics))
    )
    return (await dbsession.execute(query)).scalars()


@router.get("/{fid}/rooms", response_model=list[RoomModel])
async def get_floor_rooms(fid: int, dbsession: Annotated[AsyncSession, Depends(db_session)]) -> list[Room]:
    """Retrieve all rooms on a floor."""
    query = (
        select(Room)
        .filter(Room.floor_id == fid)
        .order_by(Room.number)
        .options(selectinload(Room.group))
        .options(selectinload(Room.floor))
        .options(selectinload(Room.items))
        .options(selectinload(Room.sample))
    )
    return (await dbsession.execute(query)).scalars()
