import asyncio
import click
import museum_map

from inspect import getfile
from pathlib import PurePath
from sqlalchemy.ext.asyncio import create_async_engine
from tornado.ioloop import  IOLoop
from tornado.web import Application, StaticFileHandler

from ..server.handlers import APICollectionHandler, APIItemHandler, APIPickHandler, FrontendHandler


@click.command()
@click.option('-p', '--port', type=int, default=6543, help='Server port')
@click.pass_context
def run(ctx, port):
    basedir = PurePath(getfile(museum_map)).parent
    engine = create_async_engine(ctx.obj['config'].get('db', 'uri'))
    app = Application(
        [
            ('/api/picks/([a-z\-]+)', APIPickHandler),
            ('/api/([a-z\-]+)', APICollectionHandler),
            ('/api/([a-z\-]+)/([0-9]+)', APIItemHandler),
            ('/images/(.*)', StaticFileHandler, {'path': ctx.obj['config'].get('images', 'basepath')}),
            ('/(.*)', FrontendHandler),
        ],
        autoreload=True,
        config=ctx.obj['config'],
        engine=engine)
    app.listen(port)
    IOLoop.current().start()


@click.group()
def server():
    pass


server.add_command(run)
