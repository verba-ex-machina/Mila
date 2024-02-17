"""Provide Mila interfaces."""

from abc import ABC, abstractmethod
from typing import List

from .types import MilaTask


class TaskIO(ABC):
    """Define the interface for a standard Mila comms channel."""

    async def __aenter__(self) -> "TaskIO":
        """Enter the comms channel."""
        await self.setup()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        """Exit the comms channel."""
        await self.teardown()

    @abstractmethod
    async def recv(self) -> List[MilaTask]:
        """Receive a list of tasks from the comms channel."""

    @abstractmethod
    async def send(self, task: MilaTask) -> None:
        """Send a task to the comms channel."""

    async def setup(self) -> None:  # Optional hook.
        """Prepare the comms channel."""

    async def teardown(self) -> None:  # Optional hook.
        """Teardown the comms channel."""


class TaskStorage(ABC):
    """Define the interface for a standard Mila storage channel."""

    @abstractmethod
    async def create(self, task: MilaTask) -> str:
        """Create a task in the storage channel."""

    @abstractmethod
    async def read(self, task_id: str) -> MilaTask:
        """Read a task from the storage channel."""

    @abstractmethod
    async def update(self, task_id: str, task: MilaTask) -> None:
        """Update a task in the storage channel."""

    @abstractmethod
    async def delete(self, task_id: str) -> None:
        """Delete a task from the storage channel."""
