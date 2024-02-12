"""Provide a fake TaskIO adapter."""

from typing import List, Union

from mila.types import MilaTask


class FakeIO:
    """Implement a fake TaskIO adapter."""

    tasks: List[MilaTask] = []

    async def recv(self) -> Union[MilaTask, None]:
        """Receive a task from FakeIO."""
        if self.tasks:
            return self.tasks.pop(0)
        return None

    async def send(self, task: MilaTask) -> None:
        """Send a task to FakeIO."""
        if task not in self.tasks:
            self.tasks.append(task)
