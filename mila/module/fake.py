"""Provide interface fakes for testing purposes."""

from typing import List

from mila.base.interfaces import TaskIO
from mila.base.types import MilaTask


class FakeIO(TaskIO):
    """Implement a fake TaskIO adapter."""

    tasks: List[MilaTask] = []

    async def recv(self) -> List[MilaTask]:
        """Receive all queued tasks from FakeIO."""
        tasks = [task.copy() for task in self.tasks]
        self.tasks.clear()
        for task in tasks:
            task.dst = task.src.copy()
        return tasks

    async def send(self, task_list: List[MilaTask]) -> None:
        """Send a list of tasks to FakeIO."""
        for task in task_list:
            if task not in self.tasks:
                self.tasks.append(task.copy())

    async def setup(self) -> None:
        """Prepare the FakeIO channel."""
        self.tasks.clear()
