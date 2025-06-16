"""Database manipulation CLI commands."""

import asyncio
import json
import os

from rich.progress import Progress
from typer import Typer

from museum_map.models import Base, Item, async_engine, async_sessionmaker

group = Typer(help="Database commands")


async def init_impl(drop_existing: bool):  # noqa: FBT001
    """Initialise the database."""
    async with async_engine.begin() as conn:
        if drop_existing:
            await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


@group.command()
def init(drop_existing: bool = False):  # noqa: FBT001, FBT002
    """Initialise the database."""
    asyncio.run(init_impl(drop_existing))


async def load_impl(source: str):
    """Load the metadata."""
    with Progress() as progress:
        task = progress.add_task("Scanning files", total=None)
        total = 0
        for _basepath, _, filenames in os.walk(source):
            for filename in filenames:
                if filename.endswith(".json"):
                    total = total + 1
        progress.update(task, total=total, completed=total)
        task = progress.add_task("Loading files", total=total)
        async with async_sessionmaker() as dbsession:
            for basepath, _, filenames in os.walk(source):
                for filename in filenames:
                    if filename.endswith(".json"):
                        with open(os.path.join(basepath, filename)) as in_f:
                            dbsession.add(Item(attributes=json.load(in_f)))
                            progress.update(task, advance=1)
                await dbsession.commit()


@group.command()
def load(source: str):
    """Load the metadata."""
    asyncio.run(load_impl(source))
