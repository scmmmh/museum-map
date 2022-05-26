import click

from sqlalchemy.ext.asyncio import create_async_engine
from tornado.ioloop import  IOLoop
from tornado.web import Application, StaticFileHandler

from ..models import create_engine
from ..server.handlers import APICollectionHandler, APIConfigHandler, APIItemHandler, APIPickHandler, FrontendHandler


@click.command()
@click.option('-p', '--port', type=int, default=6543, help='Server port')
@click.pass_context
def run(ctx, port):
    app = Application(
        [
            ('/api/picks/([a-z\-]+)', APIPickHandler),
            ('/api/config/all', APIConfigHandler, {'config': ctx.obj['config']}),
            ('/api/([a-z\-]+)', APICollectionHandler),
            ('/api/([a-z\-]+)/([0-9]+)', APIItemHandler),
            ('/images/(.*)', StaticFileHandler, {'path': ctx.obj['config']['images']['basepath']}),
            ('/(.*)', FrontendHandler),
        ],
        autoreload=True,
        config=ctx.obj['config'])
    app.listen(port)
    IOLoop.current().start()


@click.group()
def server():
    pass


server.add_command(run)
