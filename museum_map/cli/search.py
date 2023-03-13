import asyncio
import click

from meilisearch import Client
from sqlalchemy import func
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from .util import ClickIndeterminate
from ..models import Room, create_sessionmaker


async def task_completion(client, task_info):
    """Wait for an async task to complete."""
    task = client.get_task(task_info.task_uid)
    while task['status'] != 'succeeded':
        await asyncio.sleep(1)
        task = client.get_task(task_info.task_uid)


async def index_impl(config):
    """The actual indexing implementation."""
    async with create_sessionmaker(config)() as dbsession:
        client = Client(config['search']['url'], config['search']['key'])
        try:
            client.get_index('items')
            await task_completion(client, client.delete_index('items'))
        except Exception:
            pass
        await task_completion(client, client.create_index('items', {'primaryKey': 'mmap_id'}))
        items_idx = client.get_index('items')
        stmt = select(Room).options(selectinload(Room.items))
        result = await dbsession.execute(stmt)
        stmt_count = select(func.count(Room.id))
        result_count = await dbsession.execute(stmt_count)
        docs = []
        with click.progressbar(result.scalars(), length=result_count.scalar_one(), label='Indexing rooms') as progress:
            for room in progress:
                for item in room.items:
                    doc = {
                        'mmap_id': item.id,
                        'mmap_room': room.id,
                        'mmap_floor': room.floor_id,
                    }
                    doc.update(item.attributes)
                    docs.append(doc)
                    if len(docs) > 1000:
                        await task_completion(client, items_idx.add_documents(docs))
                        docs = []
        progress = ClickIndeterminate('Updating filterable attributes')
        progress.start()
        await task_completion(client, items_idx.update_filterable_attributes(['mmap_room', 'mmap_floor']))
        progress.stop()
        progress = ClickIndeterminate('Updating faceting settings')
        progress.start()
        await task_completion(client, items_idx.update_faceting_settings({
            'maxValuesPerFacet': 1000,
        }))
        progress.stop()


@click.command()
@click.pass_context
def index(ctx):
    """Index the data"""
    asyncio.run(index_impl(ctx.obj['config']))


async def pipeline_impl(config):
    """Run the search pipeline."""
    await index_impl(config)


@click.group()
def search():
    """Search generation commands."""
    pass


search.add_command(index)
