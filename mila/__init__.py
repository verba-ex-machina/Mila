"""Provide the Mila framework."""

from typing import List

from .base.interfaces import TaskIO
from .base.types import MilaTask


class MilaIO(TaskIO):
    """Define the Mila TaskIO handler."""

    tasks: List[MilaTask] = []

    async def recv(self) -> List[MilaTask]:
        """Receive a task from the Mila framework."""
        tasks = self.tasks.copy()
        self.tasks.clear()
        return tasks

    async def send(self, task: MilaTask) -> None:
        """Send a task to the Mila framework."""
        self.tasks.append(task)

    def setup(self) -> None:
        """Prepare the Mila IO channel."""
        self.tasks.clear()

    def teardown(self) -> None:
        """Teardown the Mila IO channel."""
        self.tasks.clear()
