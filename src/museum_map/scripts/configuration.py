import click

from kajiki import TextTemplate
from pkg_resources import resource_string


@click.argument('sqlalchemy_url')
@click.argument('config_uri', type=click.File('w'))
@click.option('--cache_dir', default='%(here)s/cache')
@click.option('--kajiki_mode', default='xml')
@click.option('--thread_count', default='4')
@click.option('--proxy_prefix', default='/')
@click.option('--proxy_scheme', default='http')
@click.command()
def generate_config(config_uri, **kwargs):
    """Generate a new configuration file."""
    tmpl = TextTemplate(resource_string('museum_map', 'scripts/default_configuration.txt').decode('utf-8'))
    config_uri.write(tmpl(kwargs).render())
