"""Provide Mila interfaces."""

from abc import ABC, abstractmethod
from typing import List, Union

from .types import MilaTask


class TaskIO(ABC):
    """Define the interface for a standard Mila comms channel."""

    def __enter__(self) -> "TaskIO":
        """Enter the comms channel."""
        self.setup()
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        """Exit the comms channel."""
        self.teardown()

    @abstractmethod
    async def recv(self) -> List[MilaTask]:
        """Receive a list of tasks from the comms channel."""

    @abstractmethod
    async def send(self, task: MilaTask) -> None:
        """Send a task to the comms channel."""

    def setup(self) -> None:  # Optional hook.
        """Prepare the comms channel."""

    def teardown(self) -> None:  # Optional hook.
        """Teardown the comms channel."""


class TaskStorage(ABC):
    """Define the interface for a standard Mila storage channel."""

    @abstractmethod
    async def create(self, task: MilaTask) -> str:
        """Create a task in the storage channel."""

    @abstractmethod
    async def read(self, task_id: str) -> Union[MilaTask, None]:
        """Read a task from the storage channel."""

    @abstractmethod
    async def update(self, task_id: str, task: MilaTask) -> None:
        """Update a task in the storage channel."""

    @abstractmethod
    async def delete(self, task_id: str) -> None:
        """Delete a task from the storage channel."""
