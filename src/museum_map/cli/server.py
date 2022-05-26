import click

from sqlalchemy.ext.asyncio import create_async_engine
from tornado.ioloop import  IOLoop
from tornado.web import Application, StaticFileHandler

from ..models import create_engine
from ..server.handlers import APICollectionHandler, APIConfigHandler, APIItemHandler, APIPickHandler, FrontendHandler


@click.command()
@click.pass_context
def run(ctx):
    config = ctx.obj['config']
    app = Application(
        [
            ('/api/picks/([a-z\-]+)', APIPickHandler),
            ('/api/config/all', APIConfigHandler, {'config': config}),
            ('/api/([a-z\-]+)', APICollectionHandler),
            ('/api/([a-z\-]+)/([0-9]+)', APIItemHandler),
            ('/images/(.*)', StaticFileHandler, {'path': config['images']['basepath']}),
            ('/(.*)', FrontendHandler),
        ],
        autoreload=True,
        config=config)
    app.listen(config['server']['port'], address=config['server']['host'])
    IOLoop.current().start()


@click.group()
def server():
    pass


server.add_command(run)
