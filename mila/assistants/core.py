"""Define core functionality for Mila Framework assistants."""

import json
from dataclasses import dataclass, field
from typing import Dict, Iterable

from openai.types.beta.assistant import Assistant

from mila.base.constants import LLM, STATES
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
class MilaAssistant:
    """Define a Mila assistant."""

    name: str
    description: str
    instructions: str
    tools: Iterable[MilaTool]
    model: str
    metadata: dict = field(default_factory=dict)

    async def handle_task(self, task: MilaTask) -> MilaTask:
        """Handle an incoming MilaTask."""
        assistant = await self._get_assistant()
        assistant_id = await assistant.id()
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
            assistant_id=assistant_id,
        )
        task.state = STATES.PROCESSING
        task.meta["assistant_id"] = assistant_id
        task.meta["thread_id"] = thread.id
        task.meta["run_id"] = run.id
        return task

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
