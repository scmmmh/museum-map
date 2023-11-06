"""The main Museum Map server entry-point."""
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from museum_map.server import api

app = FastAPI()

app.mount("/app", StaticFiles(packages=[("museum_map.server", "frontend/dist")], html=True), name="static")
app.include_router(api.router)


@app.get("/")
def index() -> RedirectResponse:
    """Redirect the index to the application page."""
    return RedirectResponse("/app/")
