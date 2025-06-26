"""Routes for accessing the picks data."""

import logging

from fastapi import APIRouter

from museum_map.settings import AppSettings, settings

router = APIRouter(prefix="/config")
logger = logging.getLogger(__name__)


@router.get("/", response_model=AppSettings)
async def get_config():
    """Retrieve the application configuration."""
    return settings.app.model_dump()
