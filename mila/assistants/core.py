"""Define core functionality for Mila Framework assistants."""

import asyncio
import json
from dataclasses import dataclass, field
from typing import Dict, Iterable, List

from openai.types.beta.assistant import Assistant

from mila.base.constants import LLM, STATES
from mila.base.interfaces import TaskIO
from mila.base.types import MilaTask, MilaTool

MSG_FORMAT = """
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


@dataclass
class MilaAssistant(TaskIO):
    """Define a Mila assistant."""

    # pylint: disable=too-many-instance-attributes
    name: str
    description: str
    instructions: str
    tools: Iterable[MilaTool]
    model: str
    metadata: dict = field(default_factory=dict)

    _assistant: Assistant = field(init=False)
    _id: str = field(init=False)

    async def setup(self) -> None:
        """Prepare the assistant for use."""
        self._assistant = await self._get_assistant()
        self._id = await self._assistant.id()

    async def send(self, task_list: List[MilaTask]) -> None:
        """Process tasks sent to the assistant."""
        coros = [self._handle_task(task) for task in task_list]
        await asyncio.gather(*coros)

    async def recv(self) -> List[MilaTask]:
        """Retrieve outbound responses from the assistant."""
        return []

    async def _handle_task(self, task: MilaTask) -> None:
        """Handle an incoming MilaTask."""
        thread = await LLM.beta.threads.create(
            messages=[
                {
                    "role": "user",
                    "content": (
                        " ".join(MSG_FORMAT.strip().split("\n")).format(
                            context=task.context, query=task.content
                        )
                    ),
                }
            ],
        )
        run = await LLM.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=self._id,
        )
        task.state = STATES.PROCESSING
        task.meta["assistant_id"] = self._id
        task.meta["thread_id"] = thread.id
        task.meta["run_id"] = run.id
        # The task never gets saved anywhere.

    async def _get_assistant(self) -> Assistant:
        """Retrieve an OpenAI Assistant based on this MilaAssistant."""
        assistants = await LLM.beta.assistants.list(limit=100)
        if not self.metadata.get("hash"):
            self.metadata["hash"] = hash(self)
        for assistant in assistants.data:
            if assistant.name == self.name:
                if (
                    "hash" not in assistant.metadata.keys()
                    or assistant.metadata["hash"] != self.metadata["hash"]
                ):
                    await LLM.beta.assistants.update(
                        assistant.id,
                        instructions=self.instructions,
                        tools=self.tools,
                        model=self.model,
                        metadata=self.metadata,
                    )
                return assistant
        return await LLM.beta.assistants.create(
            instructions=self.instructions,
            name=self.name,
            model=self.model,
            tools=self.tools,
            metadata=self.metadata,
        )

    def __hash__(self) -> int:
        """Return the hash of the assistant."""
        return hash(str(self))

    def __repr__(self) -> str:
        """Return the string representation of the assistant."""
        as_dict = {
            "name": self.name,
            "description": self.description,
            "instructions": self.instructions,
            "tools": [tool.definition for tool in self.tools],
            "model": self.model,
            "metadata": self.metadata,
        }
        return json.dumps(as_dict)

    def __str__(self) -> str:
        """Return the string representation of the assistant."""
        return self.__repr__()


ASSISTANTS: Dict[str, MilaAssistant] = {}


async def get_assistants() -> dict:
    """Retrieve a list of available assistants."""
    return {
        name: assistant.description for name, assistant in ASSISTANTS.items()
    }


def register_assistant(assistant: MilaAssistant) -> None:
    """Register an assistant with the framework."""
    ASSISTANTS[assistant.name] = assistant
