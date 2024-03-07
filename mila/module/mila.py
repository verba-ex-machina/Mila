"""Provide Mila Framework modules."""

from typing import List

from mila.base.constants import STATES
from mila.base.interfaces import TaskIO, TaskStorage
from mila.base.types import MilaTask


class MilaStorage(TaskStorage):
    """Mila Framework storage class."""

    async def create(self, task: MilaTask) -> str:
        """Create a task in the storage channel."""

    async def read(self, task_id: str) -> MilaTask:
        """Read a task from the storage channel."""

    async def update(self, task_id: str, task: MilaTask) -> None:
        """Update a task in the storage channel."""

    async def delete(self, task_id: str) -> None:
        """Delete a task from the storage channel."""

    async def by_state(self, state: str) -> List[MilaTask]:
        """Retrieve tasks by state from the storage channel."""
        return []


class MilaIO(TaskIO):
    """Mila Framework I/O handler class."""

    task_storage: TaskStorage

    async def recv(self) -> List[MilaTask]:
        """Receive tasks from the I/O handler."""
        return await self.task_storage.by_state(STATES.OUTBOUND)

    async def send(self, task_list: List[MilaTask]) -> None:
        """Send tasks to the I/O handler."""
        for task in task_list:
            await self.task_storage.create(task)

    async def setup(self) -> None:
        """Prepare the I/O handler."""
        self.task_storage = MilaStorage()
