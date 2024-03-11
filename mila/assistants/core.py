"""Define core functionality for Mila Framework assistants."""

import json
from dataclasses import dataclass, field
from typing import Dict, Iterable, List

from mila.base.types import MilaTask, MilaTool

PROMPT = """
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

    # pylint: disable=too-many-instance-attributes
    name: str
    description: str
    instructions: str
    tools: Iterable[MilaTool]
    model: str
    metadata: dict = field(default_factory=dict)

    async def send(self, task_list: List[MilaTask]) -> None:
        """Process tasks sent to the assistant."""
        for task in task_list:
            prompt = " ".join(
                PROMPT.strip().format(context=task.context, query=task.content)
            )
            print(prompt)

    async def recv(self) -> List[MilaTask]:
        """Retrieve outbound responses from the assistant."""
        return []

    def __hash__(self) -> int:
        """Return the hash of the assistant."""
        return hash(str(self))

    def __repr__(self) -> str:
        """Return the string representation of the assistant."""
        return json.dumps(
            {
                "name": self.name,
                "description": self.description,
                "instructions": self.instructions,
                "tools": [tool.definition for tool in self.tools],
                "model": self.model,
                "metadata": self.metadata,
            }
        )


ASSISTANTS: Dict[str, MilaAssistant] = {}


async def get_assistants() -> dict:
    """Retrieve a list of available assistants."""
    return {
        name: assistant.description for name, assistant in ASSISTANTS.items()
    }


def register_assistant(assistant: MilaAssistant) -> None:
    """Register an assistant with the framework."""
    ASSISTANTS[assistant.name] = assistant
