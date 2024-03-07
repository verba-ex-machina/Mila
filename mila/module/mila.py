"""Provide Mila Framework modules."""

from typing import List

from sqlalchemy import Engine, create_engine

from mila.base.constants import STATES
from mila.base.interfaces import TaskIO, TaskStorage
from mila.base.types import MilaTask

# from sqlalchemy.orm import (
#    DeclarativeBase,
#    Mapped,
#    Session,
#    mapped_column,
#    relationship,
# )


class MilaStorage(TaskStorage):
    """Mila Framework storage class."""

    initialized: bool = False
    engine: Engine

    async def _setup(self) -> None:
        """Initialize the storage channel."""
        print("INIT")
        self.engine = create_engine("sqlite:///:memory:", echo=True)
        self.initialized = True

    def db_required(function: callable):
        """Ensure that the database is initialized when needed."""

        async def wrapper(self, *args, **kwargs):
            """Initialize the database if needed."""
            if not self.initialized:
                await self._setup()
            return await function(self, *args, **kwargs)

        return wrapper

    @db_required
    async def create(self, task: MilaTask) -> str:
        """Create a task in the storage channel."""

    @db_required
    async def read(self, task_id: str) -> MilaTask:
        """Read a task from the storage channel."""

    @db_required
    async def update(self, task_id: str, task: MilaTask) -> None:
        """Update a task in the storage channel."""

    @db_required
    async def delete(self, task_id: str) -> None:
        """Delete a task from the storage channel."""

    @db_required
    async def by_state(self, state: str) -> List[MilaTask]:
        """Retrieve tasks by state from the storage channel."""
        return []


class MilaIO(TaskIO):
    """Mila Framework I/O handler class."""

    task_storage: TaskStorage

    async def recv(self) -> List[MilaTask]:
        """Receive tasks from the I/O handler."""
        return await self.task_storage.by_state(state=STATES.OUTBOUND)

    async def send(self, task_list: List[MilaTask]) -> None:
        """Send tasks to the I/O handler."""
        for task in task_list:
            await self.task_storage.create(task)

    async def setup(self) -> None:
        """Prepare the I/O handler."""
        self.task_storage = MilaStorage()
