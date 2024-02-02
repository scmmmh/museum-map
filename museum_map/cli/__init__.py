"""Museum Map CLI application."""
import asyncio
import logging

import click

from museum_map.cli.db import db
from museum_map.cli.groups import groups
from museum_map.cli.groups import pipeline_impl as groups_pipeline
from museum_map.cli.items import items
from museum_map.cli.items import pipeline_impl as items_pipeline
from museum_map.cli.layout import layout
from museum_map.cli.layout import pipeline_impl as layout_pipeline
from museum_map.cli.search import pipeline_impl as search_pipeline
from museum_map.cli.search import search

logger = logging.getLogger("scr")

"""
CONFIG_SCHEMA = {
    "server": {
        "type": "dict",
        "schema": {
            "host": {"type": "string", "default": "127.0.0.1"},
            "port": {"type": "integer", "default": 6543},
        },
        "default": {
            "host": "127.0.0.1",
            "port": 6543,
        },
    },
    "db": {
        "type": "dict",
        "required": True,
        "schema": {
            "dsn": {
                "type": "string",
                "required": True,
                "empty": False,
            },
        },
    },
    "search": {
        "type": "dict",
        "required": True,
        "schema": {
            "url": {
                "type": "string",
                "required": True,
                "empty": False,
            },
            "key": {
                "type": "string",
                "required": True,
                "empty": False,
            },
        },
    },
    "data": {
        "type": "dict",
        "required": True,
        "schema": {
            "topic_fields": {
                "type": "list",
                "required": True,
                "minlength": 1,
                "schema": {
                    "type": "string",
                    "empty": False,
                },
            },
            "hierarchy": {
                "type": "dict",
                "required": True,
                "schema": {
                    "field": {
                        "type": "string",
                        "required": True,
                        "empty": False,
                    },
                    "expansions": {
                        "type": "list",
                        "required": False,
                        "default": [],
                        "schema": {
                            "type": "string",
                            "allowed": ["nlp", "aat"],
                        },
                    },
                },
            },
            "year_field": {
                "type": "string",
                "required": True,
                "empty": False,
            },
        },
    },
    "images": {
        "type": "dict",
        "required": True,
        "schema": {
            "basepath": {
                "type": "string",
                "required": True,
                "empty": False,
            }
        },
    },
    "layout": {
        "type": "dict",
        "required": True,
        "schema": {
            "rooms": {
                "type": "list",
                "required": True,
                "minlength": 1,
                "schema": {
                    "type": "dict",
                    "schema": {
                        "id": {
                            "type": "string",
                            "required": True,
                            "empty": False,
                        },
                        "direction": {
                            "type": "string",
                            "required": True,
                            "allowed": ["vert", "horiz"],
                        },
                        "items": {
                            "type": "integer",
                            "required": True,
                            "min": 1,
                        },
                        "splits": {
                            "type": "integer",
                            "required": True,
                            "min": 1,
                        },
                        "position": {
                            "type": "dict",
                            "required": True,
                            "schema": {
                                "x": {"type": "integer", "required": True},
                                "y": {"type": "integer", "required": True},
                                "width": {"type": "integer", "required": True},
                                "height": {"type": "integer", "required": True},
                            },
                        },
                    },
                },
            }
        },
    },
    "app": {
        "type": "dict",
        "required": True,
        "schema": {
            "base_url": {
                "type": "string",
                "required": True,
                "empty": False,
            },
            "intro": {"type": "string", "required": True, "empty": False},
            "footer": {
                "type": "dict",
                "schema": {
                    "center": {
                        "type": "dict",
                        "schema": {
                            "label": {
                                "type": "string",
                                "required": True,
                                "empty": False,
                            },
                            "url": {
                                "type": "string",
                                "required": False,
                            },
                        },
                    },
                    "right": {
                        "type": "dict",
                        "schema": {
                            "label": {
                                "type": "string",
                                "required": True,
                                "empty": False,
                            },
                            "url": {
                                "type": "string",
                                "required": False,
                            },
                        },
                    },
                },
            },
            "item": {
                "type": "dict",
                "required": True,
                "schema": {
                    "texts": {
                        "type": "list",
                        "schema": {
                            "type": "dict",
                            "schema": {
                                "name": {
                                    "type": "string",
                                    "required": True,
                                    "empty": False,
                                },
                                "label": {
                                    "type": "string",
                                    "required": True,
                                    "empty": False,
                                },
                            },
                        },
                    },
                    "fields": {
                        "type": "list",
                        "schema": {
                            "type": "dict",
                            "schema": {
                                "name": {
                                    "type": "string",
                                    "required": True,
                                    "empty": False,
                                },
                                "label": {
                                    "type": "string",
                                    "required": True,
                                    "empty": False,
                                },
                            },
                        },
                    },
                },
            },
        },
    },
    "debug": {
        "type": "boolean",
        "default": False,
    },
    "logging": {"type": "dict"},
}
"""


@click.group()
@click.option("-v", "--verbose", count=True)
def cli(verbose: bool):  # noqa: FBT001
    """Museum Map CLI."""
    if verbose == 1:
        logging.basicConfig(level=logging.INFO)
    elif verbose > 1:
        logging.basicConfig(level=logging.DEBUG)
    logger.debug("Logging set up")


async def pipeline_impl():
    """Run the full processing pipline."""
    await items_pipeline()
    await groups_pipeline()
    await layout_pipeline()
    await search_pipeline()


@click.command()
def pipeline():
    """Run the full processing pipline."""
    asyncio.run(pipeline_impl())


cli.add_command(pipeline)
cli.add_command(db)
cli.add_command(groups)
cli.add_command(items)
cli.add_command(layout)
cli.add_command(search)
