"""Provide interfaces for Mila Framework objects."""

from abc import ABC, abstractmethod
from typing import Any, List

from mila.base.types import AssistantDefinition, MilaTask


class ContextManager(ABC):
    """Define the interface for a standard context manager."""

    async def __aenter__(self) -> "ContextManager":
        """Enter the context manager."""
        await self.setup()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        """Exit the context manager."""
        await self.teardown()

    async def setup(self) -> None:
        """Prepare the context manager."""

    async def teardown(self) -> None:
        """Teardown the context manager."""


class TaskIO(ContextManager, ABC):
    """Define the interface for a standard Mila comms channel."""

    @abstractmethod
    async def recv(self) -> List[MilaTask]:
        """Receive a list of tasks from the comms channel."""

    @abstractmethod
    async def send(self, task_list: List[MilaTask]) -> None:
        """Send a list of tasks to the comms channel."""


class MilaAssistant(TaskIO, ABC):
    """Mila Framework I/O handler class."""

    meta: AssistantDefinition = None

    def __init__(self, definition: AssistantDefinition) -> None:
        """Initialize the assistant."""
        self.meta = definition

    def __eq__(self, __value: "MilaAssistant") -> bool:
        """Compare two assistants."""
        return self.meta == __value.meta


class MilaLLM(ContextManager, ABC):
    """Mila Framework LLM interface."""

    # pylint: disable=too-few-public-methods

    @abstractmethod
    async def get_assistant(
        self, definition: AssistantDefinition
    ) -> MilaAssistant:
        """Return an assistant for the given definition."""


class TaskTracker(ContextManager, ABC):
    """Define the interface for a standard Mila task tracker."""

    @abstractmethod
    async def add(self, id: str, task: MilaTask) -> None:
        """Add a task to the tracker."""
    
    @abstractmethod
    async def get(self, id: str) -> MilaTask:
        """Get a task from the tracker."""
    
    @abstractmethod
    async def drop(self, id: str) -> None:
        """Drop a task from the tracker."""