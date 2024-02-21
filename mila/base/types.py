"""Define essential data types for Mila."""

import json
from dataclasses import asdict, dataclass, field

from mila.base.constants import STATES


@dataclass
class MilaTask:
    """Define a Mila task."""

    context: str
    content: str
    source: dict = field(default_factory=dict)
    destination: dict = field(default_factory=dict)
    state: str = STATES.NEW

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
        )
