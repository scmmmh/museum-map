"""Routes for accessing the item data."""
import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from museum_map.models import Item, ItemModel, db_session

router = APIRouter(prefix="/items")
logger = logging.getLogger(__name__)


@router.get("/", response_model=list[ItemModel])
async def get_items(
    iid: Annotated[list[int] | None, Query()],
    dbsession: Annotated[AsyncSession, Depends(db_session)],
):
    """Retrieve items."""
    query = select(Item).filter(Item.id.in_(iid)).options(selectinload(Item.group)).options(selectinload(Item.room))
    return (await dbsession.execute(query)).scalars()


@router.get("/{iid}", response_model=ItemModel)
async def get_item(iid: int, dbsession: Annotated[AsyncSession, Depends(db_session)]):
    """Fetch a single item."""
    query = select(Item).filter(Item.id == iid).options(selectinload(Item.group)).options(selectinload(Item.room))
    item = (await dbsession.execute(query)).scalar()
    if item is not None:
        return item
    else:
        raise HTTPException(404)
