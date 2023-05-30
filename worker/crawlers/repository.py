import asyncio
from typing import List, Callable

from core.abc import AbstractBaseRepository


class BaseRepository(AbstractBaseRepository):
    def __init__(self, worker_count: int):
        self.worker_count = worker_count
        self.semaphore = asyncio.Semaphore(worker_count)

    async def gather_tasks(self, tasks: List[Callable]):
        async def process_task(task):
            async with self.semaphore:
                return await task
        return await asyncio.gather(*[process_task(task) for task in tasks])
