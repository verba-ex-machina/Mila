"""Provide Mila interfaces."""

from abc import ABC, abstractmethod

from .types import MilaTask


class TaskIO(ABC):
    """Define the interface for a standard Mila comms channel."""

    @abstractmethod
    async def recv(self) -> MilaTask:
        """Receive a task from the comms channel."""

    @abstractmethod
    async def send(self, task: MilaTask) -> None:
        """Send a task to the comms channel."""


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