"""Provide fake modules for testing purposes."""

import hashlib
from typing import Dict, List, Union

from mila.base.interfaces import TaskIO, TaskStorage
from mila.base.types import MilaTask


class FakeIO(TaskIO):
    """Implement a fake TaskIO adapter."""

    tasks: List[MilaTask]

    async def recv(self) -> List[MilaTask]:
        """Receive all queued tasks from FakeIO."""
        if self.tasks:
            tasks = list(self.tasks)
            self.tasks = []
            return tasks
        return []

    async def send(self, task: MilaTask) -> None:
        """Send a task to FakeIO."""
        if task not in self.tasks:
            self.tasks.append(task)

    def setup(self) -> None:
        """Prepare the FakeIO channel."""
        self.tasks = []


class FakeStorage(TaskStorage):
    """Implement a fake TaskStorage adapter."""

    tasks: Dict[str, MilaTask] = {}

    async def create(self, task: MilaTask) -> str:
        """Create a task in FakeStorage."""
        task_id = hashlib.sha256(bytes(task)).hexdigest()
        if task_id not in self.tasks:
            self.tasks[task_id] = task
        return task_id

    async def read(self, task_id: str) -> Union[MilaTask, None]:
        """Read a task from FakeStorage."""
        return self.tasks.get(task_id, None)

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
