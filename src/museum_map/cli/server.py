import asyncio
import click

from tornado.ioloop import  IOLoop
from tornado.web import Application, StaticFileHandler

from ..models import Base, Item, Group


@click.command()
@click.pass_context
def run(ctx):
    app = Application([
        ('/(.*)', StaticFileHandler, {'path': 'src/museum_map/static', 'default_filename': 'index.html'})
    ])
    app.listen(6543)
    IOLoop.current().start()


@click.group()
def server():
    pass


server.add_command(run)
