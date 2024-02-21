"""Provide Mila framework modules."""

from typing import List

from mila.base.interfaces import TaskIO
from mila.base.types import MilaTask


class MilaIO(TaskIO):
    """Mila framework I/O handler class."""

    task_list: List[MilaTask] = []

    async def setup(self) -> None:
        """Set up the I/O handler."""

    async def teardown(self) -> None:
        """Tear down the I/O handler."""

    async def recv(self) -> List[MilaTask]:
        """Receive tasks from the I/O handler."""
        outbound_tasks = self.task_list.copy()
        self.task_list.clear()
        return outbound_tasks

    async def send(self, task_list: List[MilaTask]) -> None:
        """Send tasks to the I/O handler."""
        for task in task_list:
            # Route back to the source handler.
            task.destination = task.source.copy()
        self.task_list.extend(task_list)
