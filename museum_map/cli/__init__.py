"""Museum Map CLI application."""

import asyncio
import logging

from rich import print as output
from typer import Typer

from museum_map.__about__ import __version__
from museum_map.cli.db import group as db_group
from museum_map.cli.groups import group as groups_group
from museum_map.cli.groups import pipeline_impl as groups_pipeline
from museum_map.cli.images import group as images_group
from museum_map.cli.items import group as items_group
from museum_map.cli.items import pipeline_impl as items_pipeline
from museum_map.cli.layout import group as layout_group
from museum_map.cli.layout import pipeline_impl as layout_pipeline
from museum_map.cli.search import group as search_group
from museum_map.cli.search import pipeline_impl as search_pipeline

# from museum_map.cli.groups import groups
# from museum_map.cli.groups import pipeline_impl as groups_pipeline
# from museum_map.cli.items import items
# from museum_map.cli.items import pipeline_impl as items_pipeline
# from museum_map.cli.layout import layout
# from museum_map.cli.layout import pipeline_impl as layout_pipeline
# from museum_map.cli.search import pipeline_impl as search_pipeline
# from museum_map.cli.search import search

logger = logging.getLogger("scr")

cli = Typer()
cli.add_typer(db_group, name="db")
cli.add_typer(images_group, name="images")
cli.add_typer(items_group, name="items")
cli.add_typer(groups_group, name="groups")
cli.add_typer(layout_group, name="layout")
cli.add_typer(search_group, name="search")


@cli.command()
def version():
    """Return the current version."""
    output(__version__)


async def pipeline_impl():
    """Async full pipeline."""
    await items_pipeline()
    await groups_pipeline()
    await layout_pipeline()
    await search_pipeline()


@cli.command()
def pipeline():
    """Run the full processing pipeline."""
    asyncio.run(pipeline_impl())
