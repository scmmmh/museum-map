"""Museum Map CLI application."""

import asyncio
import logging

import click

from museum_map.cli.db import db
from museum_map.cli.groups import groups
from museum_map.cli.groups import pipeline_impl as groups_pipeline
from museum_map.cli.items import items
from museum_map.cli.items import pipeline_impl as items_pipeline
from museum_map.cli.layout import layout
from museum_map.cli.layout import pipeline_impl as layout_pipeline
from museum_map.cli.search import pipeline_impl as search_pipeline
from museum_map.cli.search import search

logger = logging.getLogger("scr")


@click.group()
@click.option("-v", "--verbose", count=True)
def cli(verbose: bool):  # noqa: FBT001
    """Museum Map CLI."""
    if verbose == 1:
        logging.basicConfig(level=logging.INFO)
    elif verbose > 1:
        logging.basicConfig(level=logging.DEBUG)
    logger.debug("Logging set up")


async def pipeline_impl():
    """Run the full processing pipline."""
    await items_pipeline()
    await groups_pipeline()
    await layout_pipeline()
    await search_pipeline()


@click.command()
def pipeline():
    """Run the full processing pipline."""
    asyncio.run(pipeline_impl())


cli.add_command(pipeline)
cli.add_command(db)
cli.add_command(groups)
cli.add_command(items)
cli.add_command(layout)
cli.add_command(search)
