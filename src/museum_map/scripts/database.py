import click

from pyramid.paster import (get_appsettings, setup_logging, )
from pyramid.scripts.common import parse_vars

from ..models.meta import Base
from ..models import get_engine


@click.command()
@click.option('--drop-existing', is_flag=True, help='Drop the existing database structure')
@click.argument('config_uri')
@click.argument('options', nargs=-1)
def init_database(config_uri, drop_existing, options):
    """Initialise the database structure."""
    options = parse_vars(options)
    setup_logging(config_uri)
    settings = get_appsettings(config_uri, options=options)

    engine = get_engine(settings)
    if drop_existing:
        Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
