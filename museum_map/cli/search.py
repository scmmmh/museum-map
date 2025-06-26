"""Search setup CLI commands."""

import asyncio
import logging

from meilisearch_python_sdk import AsyncClient
from meilisearch_python_sdk.models.settings import Faceting
from meilisearch_python_sdk.models.task import TaskInfo
from rich.progress import Progress, TaskID
from sqlalchemy import func
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typer import Typer

# from museum_map.cli.util import ClickIndeterminate
from museum_map.models import Room, async_sessionmaker
from museum_map.settings import settings

group = Typer(help="Search commands")
logger = logging.getLogger(__name__)


async def wait_for_tasks_completion(
    client: AsyncClient, tasks: list[TaskInfo], progress: Progress, progress_task: TaskID
):
    """Wait until all tasks in the list are completed."""
    completed = 0
    while completed < len(tasks):
        await asyncio.sleep(1)
        completed = 0
        for task in tasks:
            current_task = await client.get_task(task.task_uid)
            if current_task.status == "succeeded":
                completed = completed + 1
        progress.update(progress_task, completed=completed, total=len(tasks))


async def index_impl():
    """Index the full collection."""
    with Progress() as progress:
        async with async_sessionmaker() as dbsession:
            async with AsyncClient(str(settings.search.url), settings.search.key) as client:
                try:
                    index = await client.get_index("items")
                    task = await index.delete()
                    progress_task = progress.add_task("Removing existing indexes", total=None)
                    await wait_for_tasks_completion(client, [task], progress, progress_task)
                except Exception as e:
                    logger.error(e)
                items_idx = await client.create_index("items", primary_key="mmap_id")
                stmt = select(Room).options(selectinload(Room.items))
                result = await dbsession.execute(stmt)
                stmt_count = select(func.count(Room.id))
                result_count = await dbsession.execute(stmt_count)
                docs = []
                progress_task = progress.add_task("Generating room documents", total=result_count.scalar_one())
                for room in result.scalars():
                    for item in room.items:
                        doc = {
                            "mmap_id": item.id,
                            "mmap_room": room.id,
                            "mmap_floor": room.floor_id,
                        }
                        doc.update(item.attributes)
                        docs.append(doc)
                    progress.update(progress_task, advance=1)
                progress_task = progress.add_task("Waiting for indexing to complete", total=None)
                await wait_for_tasks_completion(
                    client, await items_idx.add_documents_in_batches(docs), progress, progress_task
                )
                progress.update(progress_task, total=1, completed=1)
                progress_task = progress.add_task("Updating filterable attributes", total=None)
                task = await items_idx.update_filterable_attributes(["mmap_room", "mmap_floor"])
                await wait_for_tasks_completion(client, [task], progress, progress_task)
                progress_task = progress.add_task("Updating faceting settings", total=None)
                task = await items_idx.update_faceting(Faceting(max_values_per_facet=1000))
                await wait_for_tasks_completion(client, [task], progress, progress_task)


@group.command()
def index():
    """Index the data."""
    asyncio.run(index_impl())


async def pipeline_impl():
    """Run the search pipeline."""
    await index_impl()


@group.command()
def pipeline():
    """Run the search indexing pipeline."""
    asyncio.run(index_impl())
