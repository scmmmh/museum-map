"""Routes for accessing the picks data."""

import logging
import math
from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from museum_map.models import Item, ItemModel, db_session

router = APIRouter(prefix="/picks")
logger = logging.getLogger(__name__)


@router.get("/item-of-the-day", response_model=ItemModel)
async def get_item_of_the_day(dbsession: Annotated[AsyncSession, Depends(db_session)]):
    """Retrieve the item of the day."""
    query = select(func.count()).select_from(Item)
    total = (await dbsession.execute(query)).scalar()
    row_nr = math.floor(datetime.now(tz=UTC).timestamp() / 86400) % total + 1
    query = (
        select(Item)
        .order_by(Item.id)
        .offset(row_nr)
        .limit(1)
        .options(selectinload(Item.group))
        .options(selectinload(Item.room))
    )
    item = (await dbsession.execute(query)).scalar()
    if item is not None:
        return item
    else:
        raise HTTPException(404)


@router.get("/random-items", response_model=list[ItemModel])
async def get_floors(dbsession: Annotated[AsyncSession, Depends(db_session)]):
    """Retrieve a random selection of items."""
    query = (
        select(Item)
        .order_by(func.random())
        .limit(12)
        .options(selectinload(Item.group))
        .options(selectinload(Item.room))
    )
    return (await dbsession.execute(query)).scalars()
