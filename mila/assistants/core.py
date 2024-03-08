"""Define core functionality for Mila Framework assistants."""

import json
from dataclasses import dataclass, field
from typing import Dict, Iterable

from openai.types.beta.assistant import Assistant

from mila.base.constants import LLM
from mila.base.types import MilaTool


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


ASSISTANTS: Dict[str, MilaAssistant] = {}


async def get_assistants() -> dict:
    """Retrieve a list of available assistants."""
    return {
        name: assistant.description for name, assistant in ASSISTANTS.items()
    }


def register_assistant(assistant: MilaAssistant) -> None:
    """Register an assistant with the framework."""
    ASSISTANTS[assistant.name] = assistant
