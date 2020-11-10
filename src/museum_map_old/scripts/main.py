import click

from .configuration import generate_config
from .database import init_database
from .data import load_data, generate_hierarchy, link_wikipedia


@click.group()
def cli():
    """Run the MuseumMap CLI"""
    pass

cli.add_command(init_database)
cli.add_command(load_data)
cli.add_command(generate_hierarchy)
cli.add_command(link_wikipedia)
cli.add_command(generate_config)
