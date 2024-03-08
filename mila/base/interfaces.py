"""Provide interfaces for Mila Framework objects."""

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
    async def send(self, task_list: List[MilaTask]) -> None:
        """Send a list of tasks to the comms channel."""

    async def setup(self) -> None:
        """Prepare the comms channel."""

    async def teardown(self) -> None:
        """Teardown the comms channel."""
