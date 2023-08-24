from importlib import resources

import click
from sqlalchemy.ext.asyncio import create_async_engine
from tornado.ioloop import IOLoop
from tornado.web import Application, StaticFileHandler

from museum_map.models import create_engine
from museum_map.server.handlers import (
    APICollectionHandler,
    APIConfigHandler,
    APIItemHandler,
    APIPickHandler,
    APISearchHandler,
    APIStatusHandler,
    FrontendHandler,
    create_inject_item_html,
)


@click.command()
@click.pass_context
def run(ctx):
    config = ctx.obj["config"]
    app = Application(
        [
            ("/api", APIStatusHandler),
            (r"/api/picks/([a-z\-]+)", APIPickHandler),
            ("/api/config/all", APIConfigHandler, {"config": config}),
            ("/api/search", APISearchHandler),
            (r"/api/([a-z\-]+)", APICollectionHandler),
            (r"/api/([a-z\-]+)/([0-9]+)", APIItemHandler),
            ("/images/(.*)", StaticFileHandler, {"path": config["images"]["basepath"]}),
            (
                "/(.*)",
                FrontendHandler,
                {
                    "base": resources.files("museum_map") / "server" / "frontend" / "public",
                    "html_injectors": {r"room/([0-9]+)/([0-9]+)": create_inject_item_html(config)},
                },
            ),
        ],
        autoreload=True,
        config=config,
    )
    app.listen(config["server"]["port"], address=config["server"]["host"])
    IOLoop.current().start()


@click.group()
def server():
    pass


server.add_command(run)
