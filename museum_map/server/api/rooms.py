"""Routes for accessing the room data."""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from museum_map.models import Item, ItemModel, Room, RoomModel, db_session

router = APIRouter(prefix="/rooms")
logger = logging.getLogger(__name__)


@router.get("/{rid}", response_model=RoomModel)
async def get_room(rid: int, dbsession: Annotated[AsyncSession, Depends(db_session)]) -> Room:
    """Retrieve rooms."""
    query = (
        select(Room)
        .filter(Room.id == rid)
        .options(selectinload(Room.group))
        .options(selectinload(Room.floor))
        .options(selectinload(Room.items))
        .options(selectinload(Room.sample))
    )
    room = (await dbsession.execute(query)).scalar()
    if room is not None:
        return room
    else:
        raise HTTPException(404)


@router.get("/{rid}/items", response_model=list[ItemModel])
async def get_room_items(rid: int, dbsession: Annotated[AsyncSession, Depends(db_session)]) -> list[Item]:
    """Retrieve all items in a room."""
    query = (
        (select(Item).filter(Item.room_id == rid))
        .order_by(Item.sequence)
        .options(selectinload(Item.room))
        .options(selectinload(Item.group))
    )
    return (await dbsession.execute(query)).scalars()
