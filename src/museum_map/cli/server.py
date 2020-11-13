import click

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ..models import Base, Item, Group


@click.command()
@click.pass_context
def run(ctx):
    engine = create_engine(ctx.obj['config'].get('db', 'uri'))
    Base.metadata.bind = engine
    dbsession = sessionmaker(bind=engine)()

    def output(group, indent=''):
        print(f'{indent}{group.value} ({len(group.items)})')
        for child in dbsession.query(Group).filter(Group.parent_id == group.id):
            output(child, indent=f'{indent}  ')

    for group in dbsession.query(Group).filter(Group.parent_id == None):
        output(group)


@click.group()
def server():
    pass


server.add_command(run)
