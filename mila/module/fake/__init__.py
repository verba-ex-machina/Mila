"""Provide fake modules for testing purposes."""

import hashlib
from typing import Dict, List

from mila.base.interfaces import TaskIO, TaskStorage
from mila.base.types import MilaTask


class FakeIO(TaskIO):
    """Implement a fake TaskIO adapter."""

    tasks: List[MilaTask] = []

    async def recv(self) -> List[MilaTask]:
        """Receive all queued tasks from FakeIO."""
        tasks = self.tasks.copy()
        self.tasks.clear()
        return tasks

    async def send(self, task: MilaTask) -> None:
        """Send a task to FakeIO."""
        if task not in self.tasks:
            self.tasks.append(task)

    async def setup(self) -> None:
        """Prepare the FakeIO channel."""
        self.tasks.clear()


class FakeStorage(TaskStorage):
    """Implement a fake TaskStorage adapter."""

    tasks: Dict[str, MilaTask] = {}

    async def create(self, task: MilaTask) -> str:
        """Create a task in FakeStorage."""
        task_id = hashlib.sha256(bytes(task)).hexdigest()
        if task_id in self.tasks:
            raise KeyError(
                f"Failed to create: Task with id {task_id} already exists"
            )
        self.tasks[task_id] = task
        return task_id

    async def read(self, task_id: str) -> MilaTask:
        """Read a task from FakeStorage."""
        return self.tasks[task_id]

    async def update(self, task_id: str, task: MilaTask) -> None:
        """Update a task in FakeStorage."""
        if task_id in self.tasks:
            self.tasks[task_id] = task
        else:
            raise KeyError(
                f"Failed to update: Task with id {task_id} not found"
            )

    async def delete(self, task_id: str) -> None:
        """Delete a task from FakeStorage."""
        if task_id in self.tasks:
            del self.tasks[task_id]
        else:
            raise KeyError(
                f"Failed to delete: Task with id {task_id} not found"
            )
