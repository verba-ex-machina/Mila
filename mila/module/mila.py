"""Provide Mila Framework modules."""

import asyncio
from typing import List

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from mila.assistants import ASSISTANTS
from mila.base.constants import STATES
from mila.base.interfaces import TaskIO
from mila.base.types import MilaTask


class MilaIO(TaskIO):
    """Mila Framework I/O handler class."""

    tasks: List[MilaTask] = []
    engine: AsyncEngine
    initialized: bool = False

    async def _setup(self) -> None:
        """Initialize the storage channel."""
        self.engine = create_async_engine(
            "sqlite+aiosqlite:///:memory:", echo=True
        )
        self.initialized = True

    @staticmethod
    def db_required(function: callable):
        """Ensure that the database is initialized when needed."""

        async def wrapper(self: "MilaIO", *args, **kwargs):
            """Initialize the database if needed."""
            # pylint: disable=protected-access
            # pylint: disable=not-callable
            if not self.initialized:
                await self._setup()
            return await function(self, *args, **kwargs)

        return wrapper

    @db_required
    async def recv(self) -> List[MilaTask]:
        """Receive tasks from the I/O handler."""
        outbound = [
            task for task in self.tasks if task.state == STATES.OUTBOUND
        ]
        self.tasks = [
            task for task in self.tasks if task.state != STATES.OUTBOUND
        ]
        return outbound

    @db_required
    async def send(self, task_list: List[MilaTask]) -> None:
        """Send tasks to the I/O handler."""
        # For now we're just dropping invalid tasks without notification.
        valid_tasks = [
            task for task in task_list if task.assignee in ASSISTANTS
        ]
        coros = [
            ASSISTANTS[task.assignee].handle_task(task) for task in valid_tasks
        ]
        await asyncio.gather(*coros)
        self.tasks.extend(valid_tasks)
