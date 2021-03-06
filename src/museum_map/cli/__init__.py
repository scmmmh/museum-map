import click
import logging
import os
import sys

from configparser import ConfigParser

from .db import db
from .groups import groups
from .server import server
from .items import items
from .layout import layout


logger = logging.getLogger('scr')


@click.group()
@click.option('-v', '--verbose', count=True)
@click.option('-c', '--config', default='production.ini')
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
    parser = ConfigParser()
    parser.read(config)
    ctx.obj['config'] = parser


cli.add_command(db)
cli.add_command(groups)
cli.add_command(items)
cli.add_command(server)
cli.add_command(layout)
