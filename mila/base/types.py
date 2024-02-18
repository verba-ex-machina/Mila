"""Define essential data types for Mila."""

import dataclasses
import json


@dataclasses.dataclass
class MilaTask:
    """Define a Mila task."""

    context: str
    content: str
    meta: dict = dataclasses.field(default_factory=dict)

    def __bytes__(self) -> bytes:
        """Return the bytes representation of the task."""
        return self.__repr__().encode()

    def __hash__(self) -> int:
        """Return the hash of the task."""
        return hash(str(self))

    def __repr__(self) -> str:
        """Return the string representation of the task."""
        return json.dumps(dataclasses.asdict(self))

    def __str__(self) -> str:
        """Return the string representation of the task."""
        return self.__repr__()

    def copy(self) -> "MilaTask":
        """Return a copy of the task."""
        return MilaTask(
            context=self.context,
            content=self.content,
            meta=self.meta.copy() if self.meta else {},
        )
