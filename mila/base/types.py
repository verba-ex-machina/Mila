"""Define essential Mila Framework data types."""

from dataclasses import dataclass, field
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
class UserMeta:
    """Store user metadata."""

    id: Optional[str] = None
    name: Optional[str] = None
    nick: Optional[str] = None


@dataclass
class HandlerMeta:
    """Store handler metadata."""

    handler: Optional[str] = None
    user: UserMeta = field(default_factory=UserMeta)
    meta: dict = field(default_factory=dict)

    def copy(self) -> "HandlerMeta":
        """Return a copy of the handler reference."""
        return HandlerMeta(
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
class MilaTask:
    """Define a Mila task."""

    context: str
    content: str
    src: HandlerMeta = field(default_factory=HandlerMeta)
    dst: HandlerMeta = field(default_factory=HandlerMeta)
    meta: TaskMeta = field(default_factory=TaskMeta)

    def __hash__(self) -> int:
        """Return the hash of the task."""
        return hash(str(self))

    def copy(self) -> "MilaTask":
        """Return a copy of the task."""
        return MilaTask(
            context=self.context,
            content=self.content,
            src=self.src.copy(),
            dst=self.dst.copy(),
            meta=self.meta.copy(),
        )
