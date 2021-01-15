import click
import json
import os
import shutil
import subprocess

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ..models import Base, Item


@click.command()
@click.option('--drop-existing', is_flag=True, help='Drop any existing tables.')
@click.pass_context
def init(ctx, drop_existing):
    """Initialise the database."""
    engine = create_engine(ctx.obj['config'].get('db', 'uri'))
    Base.metadata.bind = engine
    if drop_existing:
        Base.metadata.drop_all()
    Base.metadata.create_all()


@click.command()
@click.argument('source')
@click.pass_context
def load(ctx, source):
    """Load the metadata."""
    engine = create_engine(ctx.obj['config'].get('db', 'uri'))
    Base.metadata.bind = engine
    dbsession = sessionmaker(bind=engine)()
    for basepath, _, filenames in os.walk(source):
        for filename in filenames:
            if filename.endswith('.json'):
                with open(os.path.join(basepath, filename)) as in_f:
                    dbsession.add(Item(attributes=json.load(in_f)))
    dbsession.commit()


@click.command()
@click.argument('source')
@click.argument('target')
@click.pass_context
def load_images(ctx, source, target):
    """Load and convert images."""
    for basepath, _, filenames in os.walk(source):
        for filename in filenames:
            if filename.endswith('.jpg'):
                image_id = filename[:filename.find('.')]
                os.makedirs(os.path.join(target, *image_id), exist_ok=True)
                image_source = os.path.join(basepath, filename)
                image_target = os.path.join(target, *image_id, filename)
                shutil.copy(image_source, image_target)
                subprocess.run(['gm', 'convert', image_source, '-resize', '240x240', image_target.replace('.jpg', '-240.jpg')])
                subprocess.run(['gm', 'convert', image_source, '-resize', '320x320', image_target.replace('.jpg', '-320.jpg')])


@click.group()
def db():
    """Database administration."""
    pass


db.add_command(init)
db.add_command(load)
db.add_command(load_images)
