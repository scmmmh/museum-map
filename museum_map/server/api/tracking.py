"""Routes for accessing the room data."""
import logging
from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Depends
from pydantic import UUID4, BaseModel
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from museum_map.models import LogEntry, User, UserModel, db_session

router = APIRouter(prefix="/tracking")
logger = logging.getLogger(__name__)


@router.post("/register", response_model=UserModel)
async def register_user(dbsession: Annotated[AsyncSession, Depends(db_session)]) -> User:
    """Register a new tracking user."""
    user = User(public_id=str(uuid4()))
    dbsession.add(user)
    await dbsession.commit()
    return user


@router.delete("/{uid}", status_code=204)
async def delete_user(uid: UUID4, dbsession: Annotated[AsyncSession, Depends(db_session)]) -> None:
    """Delete a user and all their logs."""
    query = select(User).filter(User.public_id == str(uid))
    user = (await dbsession.execute(query)).scalar()
    if user:
        query = delete(LogEntry).filter(LogEntry.user_id == user.id)
        await dbsession.execute(query)
        await dbsession.delete(user)
        await dbsession.commit()


class TrackingAction(BaseModel):
    """A single tracked action."""

    action: str
    timestamp: float
    params: dict


@router.post("/track/{uid}", status_code=204)
async def track_activities(
    uid: UUID4, actions: list[TrackingAction], dbsession: Annotated[AsyncSession, Depends(db_session)]
) -> None:
    """Store the activities for the tracking user."""
    query = select(User).filter(User.public_id == str(uid))
    user = (await dbsession.execute(query)).scalar()
    if user:
        for action in actions:
            dbsession.add(
                LogEntry(user_id=user.id, action=action.action, timestamp=action.timestamp, params=action.params)
            )
        await dbsession.commit()
