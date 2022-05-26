import asyncio
import click
import logging
import os
import sys
import yaml

from .db import db
from .groups import groups, pipeline_impl as groups_pipeline
from .server import server
from .items import items, pipeline_impl as items_pipeline
from .layout import layout, pipeline_impl as layout_pipeline


logger = logging.getLogger('scr')


@click.group()
@click.option('-v', '--verbose', count=True)
@click.option('-c', '--config', default='production.yml')
@click.pass_context
def cli(ctx, verbose, config):
    """Museum Map CLI"""
    ctx.ensure_object(dict)
    if verbose == 1:
        logging.basicConfig(level=logging.INFO)
    elif verbose > 1:
        logging.basicConfig(level=logging.DEBUG)
    logger.debug('Logging set up')
    if not os.path.exists(config):
        logger.error(f'Configuration file {config} not found')
        sys.exit(1)
    with open(config) as in_f:
        config = yaml.load(in_f, Loader=yaml.FullLoader)
        ctx.obj['config'] = config


async def pipeline_impl(config):
    """Run the full processing pipline."""
    await items_pipeline(config)
    await groups_pipeline(config)
    await layout_pipeline(config)


@click.command()
@click.pass_context
def pipeline(ctx):
    """Run the full processing pipline."""
    asyncio.run(pipeline_impl(ctx.obj['config']))

cli.add_command(pipeline)
cli.add_command(db)
cli.add_command(groups)
cli.add_command(items)
cli.add_command(server)
cli.add_command(layout)
