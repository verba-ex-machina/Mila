"""Define essential Mila Framework data types."""

import json
from dataclasses import asdict, dataclass, field
from typing import Optional

from mila.base.constants import STATES


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
class MilaTask:
    """Define a Mila task."""

    context: str
    content: str
    source: dict = field(default_factory=dict)
    destination: dict = field(default_factory=dict)
    state: str = STATES.NEW
    meta: dict = field(default_factory=dict)
    assignee: Optional[str] = "Overmind"  # Unassigned? Overmind.

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
