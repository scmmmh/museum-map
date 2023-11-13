"""Routes for accessing the floor topics data."""
import logging
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from museum_map.models import FloorTopic, FloorTopicModel, db_session

router = APIRouter(prefix="/floor-topics")
logger = logging.getLogger(__name__)


@router.get("/", response_model=list[FloorTopicModel])
async def get_floor_topics(dbsession: Annotated[AsyncSession, Depends(db_session)]) -> list[FloorTopic]:
    """Retrieve all floor topics."""
    query = select(FloorTopic).options(selectinload(FloorTopic.group)).options(selectinload(FloorTopic.floor))
    return (await dbsession.execute(query)).scalars()
