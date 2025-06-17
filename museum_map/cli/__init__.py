"""Museum Map CLI application."""

import logging

from rich import print as output
from typer import Typer

from museum_map.__about__ import __version__
from museum_map.cli.db import group as db_group
from museum_map.cli.images import group as images_group
from museum_map.cli.items import group as items_group

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


@cli.command()
def version():
    """Return the current version."""
    output(__version__)
