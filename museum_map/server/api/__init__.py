from fastapi import APIRouter

from museum_map.__about__ import __version__


router = APIRouter(prefix="/api")


@router.get("/")
def index() -> dict():
    return {"ready": False, "version": __version__}
