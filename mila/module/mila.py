"""Provide Mila framework modules."""

from typing import List

from mila.base.constants import STATES
from mila.base.interfaces import TaskIO
from mila.base.types import MilaTask
from mila.module.fake import FakeStorage


class MilaIO(TaskIO):
    """Mila framework I/O handler class."""

    task_storage = FakeStorage()  # Replace with real storage.

    async def recv(self) -> List[MilaTask]:
        """Receive tasks from the I/O handler."""
        return await self.task_storage.by_state(STATES.OUTBOUND)

    async def send(self, task_list: List[MilaTask]) -> None:
        """Send tasks to the I/O handler."""
        for task in task_list:
            await self.task_storage.create(task)
