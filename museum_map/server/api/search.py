"""Routes for searching the index."""
import logging
from typing import Annotated

from fastapi import APIRouter, Query
from meilisearch_python_async import Client

from museum_map.settings import settings

router = APIRouter(prefix="/search")
logger = logging.getLogger(__name__)


client = Client(str(settings.search.url), settings.search.key)
index = None


@router.get("/")
async def search(q: Annotated[str, Query()]):
    """Run the search for floors and rooms."""
    global index  # noqa: PLW0603
    if index is None:
        index = await client.get_index("items")
    result = await index.search(
        q,
        limit=1,
        facets=["mmap_room", "mmap_floor"],
    )
    facets = result.facet_distribution
    return {
        "floors": [int(key) for key in facets["mmap_floor"].keys()],
        "rooms": [int(key) for key in facets["mmap_room"].keys()],
    }


@router.get("/room/{rid}")
async def room_search(rid: int, q: Annotated[str, Query()]):
    """Run the search for items in a specific room."""
    global index  # noqa: PLW0603
    if index is None:
        index = await client.get_index("items")
    result = await index.search(
        q,
        limit=150,
        filter=[f"mmap_room = {rid!s}"],
    )
    return {
        "items": [item["mmap_id"] for item in result.hits],
    }
