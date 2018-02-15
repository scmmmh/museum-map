import click

from .database import initdb
from .data import load_data, generate_hierarchy


@click.group()
def cli():
    """Run the MuseumMap CLI"""
    pass

cli.add_command(initdb)
cli.add_command(load_data)
cli.add_command(generate_hierarchy)
