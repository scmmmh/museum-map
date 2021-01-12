import asyncio
import click

from sqlalchemy.ext.asyncio import create_async_engine
from tornado.ioloop import  IOLoop
from tornado.web import Application, StaticFileHandler

from ..models import Base, Item, Group

from ..server.handlers import APICollectionHandler, APIItemHandler


@click.command()
@click.pass_context
def run(ctx):
    engine = create_async_engine(ctx.obj['config'].get('db', 'uri'))
    app = Application(
        [
            ('/api/([a-z]+)', APICollectionHandler),
            ('/api/([a-z]+)/([0-9]+)', APIItemHandler),
            ('/images/(.*)', StaticFileHandler, {'path': ctx.obj['config'].get('images', 'basepath')}),
            ('/(.*)', StaticFileHandler, {'path': 'src/museum_map/static', 'default_filename': 'index.html'})
        ],
        autoreload=True,
        config=ctx.obj['config'],
        engine=engine)
    app.listen(6543)
    IOLoop.current().start()


@click.group()
def server():
    pass


server.add_command(run)
