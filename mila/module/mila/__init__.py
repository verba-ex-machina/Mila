"""Provide Mila framework modules."""

from typing import List

from mila.assistants import ASSISTANTS
from mila.base.interfaces import TaskIO
from mila.base.types import MilaTask


class MilaIO(TaskIO):
    """Mila framework I/O handler class."""

    task_list: List[MilaTask] = []

    async def recv(self) -> List[MilaTask]:
        """Receive tasks from the I/O handler."""
        # This is just an echo server for now.
        outbound_tasks = self.task_list.copy()
        self.task_list.clear()
        return outbound_tasks

    async def send(self, task_list: List[MilaTask]) -> None:
        """Send tasks to the I/O handler."""
        for task in task_list:
            # Yet another echo server implementation (for now).
            task.destination = task.source.copy()
        self.task_list.extend(task_list)
