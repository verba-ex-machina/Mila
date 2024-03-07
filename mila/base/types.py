"""Define essential Mila Framework data types."""

import json
from dataclasses import asdict, dataclass, field
from typing import Iterable, Optional

from openai.types.beta.assistant import Assistant

from mila.base.constants import LLM, STATES


@dataclass
class MilaTool:
    """Define a single tool in an Assistant's toolkit."""

    name: str
    function: callable
    properties: dict = field(default_factory=dict)
    required: list = field(default_factory=list)

    @property
    def definition(self) -> dict:
        """Get the tool definition."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.function.__doc__,
                "parameters": {
                    "type": "object",
                    "properties": self.properties,
                    "required": self.required,
                },
            },
        }


@dataclass
class MilaAssistant:
    """Define a Mila assistant."""

    name: str
    description: str
    instructions: str
    tools: Iterable[MilaTool]
    model: str
    metadata: dict = field(default_factory=dict)

    async def spawn(self) -> Assistant:
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


@dataclass
class MilaTask:
    """Define a Mila task."""

    context: str
    content: str
    source: dict = field(default_factory=dict)
    destination: dict = field(default_factory=dict)
    state: str = STATES.NEW
    meta: dict = field(default_factory=dict)
    assignee: Optional[str] = "Overmind"  # Unassigned? Overmind.

    def __bytes__(self) -> bytes:
        """Return the bytes representation of the task."""
        return self.__repr__().encode()

    def __hash__(self) -> int:
        """Return the hash of the task."""
        return hash(str(self))

    def __repr__(self) -> str:
        """Return the string representation of the task."""
        return json.dumps(asdict(self))

    def __str__(self) -> str:
        """Return the string representation of the task."""
        return self.__repr__()

    def copy(self) -> "MilaTask":
        """Return a copy of the task."""
        return MilaTask(
            context=self.context,
            content=self.content,
            source=self.source.copy(),
            destination=self.destination.copy(),
            state=self.state,
            meta=self.meta.copy(),
            assignee=self.assignee,
        )
