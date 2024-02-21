"""Define essential data types for Mila."""

import json
from dataclasses import asdict, dataclass, field


@dataclass
class MilaTaskStates:
    """Define a set of statuses for a Mila task."""

    # pylint: disable=C0103

    NEW: str = "new"
    COMPLETE: str = "complete"


@dataclass
class MilaTaskMeta:
    """Define metadata for a Mila task."""

    source: dict = field(default_factory=dict)
    destination: dict = field(default_factory=dict)
    state: str = MilaTaskStates.NEW

    def copy(self) -> "MilaTaskMeta":
        """Return a copy of the metadata."""
        return MilaTaskMeta(
            source=self.source.copy(),
            destination=self.destination.copy(),
            state=str(self.state),
        )


@dataclass
class MilaTask:
    """Define a Mila task."""

    context: str
    content: str
    meta: MilaTaskMeta = field(default_factory=MilaTaskMeta)
    # Provide a standard set of states.
    states: MilaTaskStates = field(default_factory=MilaTaskStates)

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
            meta=self.meta.copy(),
        )
