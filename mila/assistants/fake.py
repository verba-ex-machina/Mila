"""Provide a FakeAssistant implementation."""

from typing import List

from mila.base.interfaces import MilaAssistant, TaskIO
from mila.base.types import AssistantDefinition, MilaTask
from mila.io.fake import FakeIO


class FakeAssistant(MilaAssistant):
    """Define the FakeAssistant class."""

    _fakeio: TaskIO

    def __init__(self, definition: AssistantDefinition) -> None:
        """Initialize the FakeAssistant."""
        super().__init__(definition)
        self._fakeio = FakeIO()

    async def send(self, task_list: List[MilaTask]) -> None:
        """Send a list of tasks to the FakeAssistant."""
        await self._fakeio.send(task_list)

    async def recv(self) -> List[MilaTask]:
        """Receive all queued tasks from the FakeAssistant."""
        return await self._fakeio.recv()
