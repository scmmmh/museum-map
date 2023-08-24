import asyncio
import json
import os
import shutil
import subprocess

import click

from museum_map.cli.util import ClickIndeterminate
from museum_map.models import Base, Item, create_engine, create_sessionmaker


async def init_impl(config, drop_existing):
    """Initialise the database."""
    engine = create_engine(config)
    async with engine.begin() as conn:
        if drop_existing:
            await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


@click.command()
@click.option("--drop-existing", is_flag=True, help="Drop any existing tables.")
@click.pass_context
def init(ctx, drop_existing):
    """Initialise the database."""
    asyncio.run(init_impl(ctx.obj["config"], drop_existing))


async def load_impl(config, source):
    """Load the metadata."""
    progress = ClickIndeterminate("Loading items")
    progress.start()
    async with create_sessionmaker(config)() as dbsession:
        for basepath, _, filenames in os.walk(source):
            for filename in filenames:
                if filename.endswith(".json"):
                    with open(os.path.join(basepath, filename)) as in_f:
                        dbsession.add(Item(attributes=json.load(in_f)))
            await dbsession.commit()
    progress.stop()


@click.command()
@click.argument("source")
@click.pass_context
def load(ctx, source):
    """Load the metadata."""
    asyncio.run(load_impl(ctx.obj["config"], source))


@click.command()
@click.argument("source")
@click.argument("target")
@click.pass_context
def load_images(ctx, source, target):  # noqa: ARG001
    """Load and convert images."""
    progress = ClickIndeterminate("Loading images")
    progress.start()
    for basepath, _, filenames in os.walk(source):
        for filename in filenames:
            if filename.endswith(".jpg"):
                image_id = filename[: filename.find(".")]
                os.makedirs(os.path.join(target, *image_id), exist_ok=True)
                image_source = os.path.join(basepath, filename)
                image_target = os.path.join(target, *image_id, filename)
                shutil.copy(image_source, image_target)
                subprocess.run(
                    [  # noqa: S603 S607
                        "gm",
                        "convert",
                        image_source,
                        "-resize",
                        "240x240",
                        image_target.replace(".jpg", "-240.jpg"),
                    ],
                    check=True,
                )
                subprocess.run(
                    [  # noqa: S603 S607
                        "gm",
                        "convert",
                        image_source,
                        "-resize",
                        "320x320",
                        image_target.replace(".jpg", "-320.jpg"),
                    ],
                    check=True,
                )
    progress.stop()


@click.group()
def db():
    """Database administration."""
    pass


db.add_command(init)
db.add_command(load)
db.add_command(load_images)
