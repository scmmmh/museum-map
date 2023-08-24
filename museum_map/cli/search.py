import asyncio
import click

from meilisearch_python_async import Client
from meilisearch_python_async.models.settings import Faceting
from meilisearch_python_async.task import wait_for_task
from sqlalchemy import func
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from .util import ClickIndeterminate
from ..models import Room, create_sessionmaker


async def index_impl(config):
    """The actual indexing implementation."""
    async with create_sessionmaker(config)() as dbsession:
        async with Client(config['search']['url'], config['search']['key']) as client:
            try:
                index = await client.get_index('items')
                task = await index.delete()
                await wait_for_task(client, task.task_uid, timeout_in_ms=None)
            except Exception:
                pass
            items_idx = await client.create_index('items', primary_key='mmap_id')
            stmt = select(Room).options(selectinload(Room.items))
            result = await dbsession.execute(stmt)
            stmt_count = select(func.count(Room.id))
            result_count = await dbsession.execute(stmt_count)
            docs = []
            with click.progressbar(result.scalars(), length=result_count.scalar_one(), label='Generating rooms documents') as progress:
                for room in progress:
                    for item in room.items:
                        doc = {
                            'mmap_id': item.id,
                            'mmap_room': room.id,
                            'mmap_floor': room.floor_id,
                        }
                        doc.update(item.attributes)
                        docs.append(doc)
            tasks = await items_idx.add_documents_in_batches(docs)
            with click.progressbar(tasks, label='Waiting for indexing to complete') as progress:
                for task in progress:
                    await wait_for_task(client, task.task_uid, timeout_in_ms=None, interval_in_ms=1000)
            progress = ClickIndeterminate('Updating filterable attributes')
            progress.start()
            task = await items_idx.update_filterable_attributes(['mmap_room', 'mmap_floor'])
            await wait_for_task(client, task.task_uid, timeout_in_ms=None, interval_in_ms=1000)
            progress.stop()
            progress = ClickIndeterminate('Updating faceting settings')
            progress.start()
            task = await items_idx.update_faceting(Faceting(max_values_per_facet=1000))
            await wait_for_task(client, task.task_uid, timeout_in_ms=None, interval_in_ms=1000)
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
