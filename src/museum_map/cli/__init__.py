import asyncio
import click
import logging
import os
import sys
import yaml

from cerberus import Validator
from typing import Union

from .db import db
from .groups import groups, pipeline_impl as groups_pipeline
from .server import server
from .items import items, pipeline_impl as items_pipeline
from .layout import layout, pipeline_impl as layout_pipeline


logger = logging.getLogger('scr')

CONFIG_SCHEMA = {
    'server': {
        'type': 'dict',
        'schema': {
            'host': {
                'type': 'string',
                'default': '127.0.0.1'
            },
            'port': {
                'type': 'integer',
                'default': 6543
            },
        },
        'default': {
            'host': '127.0.0.1',
            'port': 6543,
        }
    },
    'db': {
        'type': 'dict',
        'required': True,
        'schema': {
            'dsn': {
                'type': 'string',
                'required': True,
                'empty': False,
            },
        }
    },
    'data': {
        'type': 'dict',
        'required': True,
        'schema': {
            'topic_fields': {
                'type': 'list',
                'required': True,
                'minlength': 1,
                'schema': {
                    'type': 'string',
                    'empty': False,
                }
            },
            'hierarchy': {
                'type': 'dict',
                'required': True,
                'schema': {
                    'field': {
                        'type': 'string',
                        'required': True,
                        'empty': False,
                    },
                    'expansions': {
                        'type': 'list',
                        'required': False,
                        'default': [],
                        'schema': {
                            'type': 'string',
                            'allowed': ['nlp', 'aat'],
                        }
                    }
                }
            },
            'year_field': {
                'type': 'string',
                'required': True,
                'empty': False,
            }
        }
    },
    'images': {
        'type': 'dict',
        'required': True,
        'schema': {
            'basepath': {
                'type': 'string',
                'required': True,
                'empty': False,
            }
        }
    },
    'layout': {
        'type': 'dict',
        'required': True,
        'schema': {
            'rooms': {
                'type': 'list',
                'required': True,
                'minlength': 1,
                'schema': {
                    'type': 'dict',
                    'schema': {
                        'id': {
                            'type': 'string',
                            'required': True,
                            'empty': False,
                        },
                        'direction': {
                            'type': 'string',
                            'required': True,
                            'allowed': ['vert', 'horiz'],
                        },
                        'items': {
                            'type': 'integer',
                            'required': True,
                            'min': 1,
                        },
                        'splits': {
                            'type': 'integer',
                            'required': True,
                            'min': 1,
                        },
                        'position': {
                            'type': 'string',
                            'required': True,
                            'empty': False,
                        }
                    }
                }
            }
        }
    },
    'app': {
        'type': 'dict',
        'required': True,
        'schema': {
            'intro': {
                'type': 'string',
                'required': True,
                'empty': False
            },
            'footer': {
                'type': 'dict',
                'schema': {
                    'center': {
                        'type': 'dict',
                        'schema': {
                            'label': {
                                'type': 'string',
                                'required': True,
                                'empty': False,
                            },
                            'url': {
                                'type': 'string',
                                'required': False,
                            }
                        }
                    },
                    'right': {
                        'type': 'dict',
                        'schema': {
                            'label': {
                                'type': 'string',
                                'required': True,
                                'empty': False,
                            },
                            'url': {
                                'type': 'string',
                                'required': False,
                            }
                        }
                    }
                }
            },
            'item': {
                'type': 'dict',
                'required': True,
                'schema': {
                    'texts': {
                        'type': 'list',
                        'schema': {
                            'type': 'dict',
                            'schema': {
                                'name': {
                                    'type': 'string',
                                    'required': True,
                                    'empty': False,
                                },
                                'label': {
                                    'type': 'string',
                                    'required': True,
                                    'empty': False,
                                }
                            }
                        }
                    },
                    'fields': {
                        'type': 'list',
                        'schema': {
                            'type': 'dict',
                            'schema': {
                                'name': {
                                    'type': 'string',
                                    'required': True,
                                    'empty': False,
                                },
                                'label': {
                                    'type': 'string',
                                    'required': True,
                                    'empty': False,
                                }
                            }
                        }
                    }
                }
            }
        }
    },
    'debug': {
        'type': 'boolean',
        'default': False,
    },
    'logging': {
        'type': 'dict'
    }
}


def validate_config(config: dict) -> dict:
    """Validate the configuration.

    :param config: The configuration to validate
    :type config: dict
    :return: The validated and normalised configuration
    :rtype: dict
    """
    validator = Validator(CONFIG_SCHEMA)
    if validator.validate(config):
        return validator.normalized(config)
    else:
        error_list = []

        def walk_error_tree(err: Union[dict, list], path: str) -> None:
            if isinstance(err, dict):
                for key, value in err.items():
                    walk_error_tree(value, path + (str(key), ))
            elif isinstance(err, list):
                for sub_err in err:
                    walk_error_tree(sub_err, path)
            else:
                error_list.append(f'{".".join(path)}: {err}')

        walk_error_tree(validator.errors, ())
        error_str = '\n'.join(error_list)
        raise click.ClickException(f'Configuration errors:\n\n{error_str}')


@click.group()
@click.option('-v', '--verbose', count=True)
@click.option('-c', '--config', default='production.yml')
@click.pass_context
def cli(ctx, verbose, config):
    """Museum Map CLI"""
    ctx.ensure_object(dict)
    if verbose == 1:
        logging.basicConfig(level=logging.INFO)
    elif verbose > 1:
        logging.basicConfig(level=logging.DEBUG)
    logger.debug('Logging set up')
    if not os.path.exists(config):
        logger.error(f'Configuration file {config} not found')
        sys.exit(1)
    with open(config) as in_f:
        config = yaml.load(in_f, Loader=yaml.FullLoader)
        ctx.obj['config'] = validate_config(config)


async def pipeline_impl(config):
    """Run the full processing pipline."""
    await items_pipeline(config)
    await groups_pipeline(config)
    await layout_pipeline(config)


@click.command()
@click.pass_context
def pipeline(ctx):
    """Run the full processing pipline."""
    asyncio.run(pipeline_impl(ctx.obj['config']))

cli.add_command(pipeline)
cli.add_command(db)
cli.add_command(groups)
cli.add_command(items)
cli.add_command(server)
cli.add_command(layout)
