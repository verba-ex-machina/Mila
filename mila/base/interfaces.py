"""Provide interfaces for Mila Framework objects."""

from abc import ABC, abstractmethod
from typing import List

from .types import MilaAssistant, MilaTask


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


BASE_PROMPT = """
A new request has arrived. Here is the context:

```
{context}
```

Here is the request:

> {query}

Please respond appropriately to the user's request, per the terms of your
instructions. Use whatever tools are at your disposal to provide the best
possible response. If you need help, you can ask other assistants for their
input by delegating tasks to them. If you encounter problems, report them
in your response.
"""


class AssistantBase(TaskIO):
    """Mila Framework I/O handler class."""

    meta: MilaAssistant = None

    def __init__(self, assistant: MilaAssistant) -> None:
        """Initialize the assistant."""
        self.meta = assistant

    async def send(self, task_list: List[MilaTask]) -> None:
        """Process tasks sent to the assistant."""
        for task in task_list:
            print(
                BASE_PROMPT.strip().format(
                    context=task.context, query=task.content
                )
            )

    async def recv(self) -> List[MilaTask]:
        """Retrieve outbound responses from the assistant."""
        return []
