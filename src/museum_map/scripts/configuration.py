import click

from kajiki import TextTemplate
from pkg_resources import resource_string


@click.argument('sqlalchemy-url')
@click.argument('config-uri', type=click.File('w'))
@click.option('--cache-dir', default='%(here)s/cache')
@click.option('--kajiki-mode', default='xml')
@click.option('--thread-count', default='4')
@click.option('--proxy-prefix', default='/')
@click.option('--proxy-scheme', default='http')
@click.option('--more-info-url', default='http://informatik.uni-halle.de')
@click.option('--host', default='127.0.0.1')
@click.option('--port', default='%(http_port)s')
@click.command()
def generate_config(config_uri, **kwargs):
    """Generate a new configuration file."""
    tmpl = TextTemplate(resource_string('museum_map', 'scripts/default_configuration.txt').decode('utf-8'))
    config_uri.write(tmpl(kwargs).render())
