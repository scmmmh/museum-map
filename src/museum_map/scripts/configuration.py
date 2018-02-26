import click

from kajiki import TextTemplate
from pkg_resources import resource_string


@click.argument('config_uri', type=click.File('w'))
@click.argument('sqlalchemy_url')
@click.option('--cache_dir', default='%(here)s/cache_dir')
@click.option('--kajiki_mode', default='xml')
@click.command()
def generate_config(config_uri, **kwargs):
    """Generate a new configuration file."""
    tmpl = TextTemplate(resource_string('museum_map', 'scripts/default_configuration.txt').decode('utf-8'))
    config_uri.write(tmpl(kwargs).render())
