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
class UserReference:
    """Represent a user associated with a given task."""

    id: Optional[str] = None
    name: Optional[str] = None
    nick: Optional[str] = None


@dataclass
class HandlerReference:
    """Store reference information about the assigned IO handler."""

    user: UserReference = field(default_factory=UserReference)
    handler: Optional[str] = None
    meta: dict = field(default_factory=dict)

    def copy(self) -> "HandlerReference":
        """Return a copy of the handler reference."""
        return HandlerReference(
            handler=self.handler,
            user=self.user,
            meta=self.meta.copy(),
        )


@dataclass
class MilaTask:
    """Define a Mila task."""

    context: str
    content: str
    state: str = STATES.NEW
    source: HandlerReference = field(default_factory=HandlerReference)
    destination: HandlerReference = field(default_factory=HandlerReference)
    assignee: Optional[str] = None

    def __hash__(self) -> int:
        """Return the hash of the task."""
        return hash(str(self))

    def copy(self) -> "MilaTask":
        """Return a copy of the task."""
        return MilaTask(
            context=self.context,
            content=self.content,
            state=self.state,
            source=self.source.copy(),
            destination=self.destination.copy(),
            assignee=self.assignee,
        )
