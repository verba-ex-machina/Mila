"""Define essential Mila Framework data types."""

import json
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional

from mila.base.constants import STATES


@dataclass
class ToolProperty:
    """Define a single property in a tool."""

    name: str
    type: str
    description: Optional[str] = None
    enum: Optional[List[str]] = None

    @property
    def definition(self) -> dict:
        """Get the property definition."""
        definition = {
            "type": self.type,
        }
        if self.description:
            definition["description"] = self.description
        if self.enum:
            definition["enum"] = self.enum
        return definition


@dataclass
class Tool:
    """Define a single tool in an Assistant's toolkit."""

    name: str
    function: callable
    properties: List[ToolProperty] = field(default_factory=list)
    required: List[str] = field(default_factory=list)

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
                    "properties": {
                        prop.name: prop.definition for prop in self.properties
                    },
                    "required": self.required,
                },
            },
        }


@dataclass
class User:
    """Store user metadata."""

    id: Optional[str] = None
    name: Optional[str] = None
    nick: Optional[str] = None


@dataclass
class Handler:
    """Store handler metadata."""

    handler: Optional[str] = None
    user: User = field(default_factory=User)
    meta: dict = field(default_factory=dict)

    def copy(self) -> "Handler":
        """Return a copy of the handler reference."""
        return Handler(
            handler=self.handler,
            user=self.user,
            meta=self.meta.copy(),
        )


@dataclass
class TaskMeta:
    """Store task metadata."""

    state: str = STATES.NEW
    assignment: Optional[str] = None

    def copy(self) -> "TaskMeta":
        """Return a copy of the task metadata."""
        return TaskMeta(
            state=self.state,
            assignment=self.assignment,
        )


@dataclass
class Task:
    """Define a Mila task."""

    context: str
    content: str
    src: Handler = field(default_factory=Handler)
    dst: Handler = field(default_factory=Handler)
    meta: TaskMeta = field(default_factory=TaskMeta)

    def __hash__(self) -> int:
        """Return the hash of the task."""
        return hash(str(self))

    def copy(self) -> "Task":
        """Return a copy of the task."""
        return Task(
            context=self.context,
            content=self.content,
            src=self.src.copy(),
            dst=self.dst.copy(),
            meta=self.meta.copy(),
        )


@dataclass
class AssistantDefinition:
    """Define a Mila assistant."""

    name: str
    description: str
    instructions: str
    tools: Iterable[Tool]
    model: str
    metadata: Dict[str, str] = field(default_factory=dict)

    @staticmethod
    def _format(original: str) -> str:
        """Format input according to rules."""
        stripped = "\n".join([line.strip() for line in original.split("\n")])
        paragraphs = stripped.split("\n\n")
        return "\n\n".join(
            [
                " ".join([line.strip() for line in paragraph.split("\n")])
                for paragraph in paragraphs
            ]
        ).strip()

    def __hash__(self) -> int:
        """Return the hash of the assistant."""
        return hash(str(self))

    def __repr__(self) -> str:
        """Return the string representation of the assistant."""
        return json.dumps(
            {
                "name": self.name,
                "description": self.description,
                "instructions": self._format(self.instructions),
                "tools": [tool.definition for tool in self.tools],
                "model": self.model,
                "metadata": self.metadata,
            }
        )
