"""Provide a fake TaskStorage adapter."""

import hashlib
from typing import Dict, Union

from mila.types import MilaTask


class FakeStorage:
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
