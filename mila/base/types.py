"""Define essential data types for Mila."""

import dataclasses
import json
from typing import Optional


@dataclasses.dataclass
class MilaTask:
    """Define a Mila task."""

    context: str
    content: str
    meta: Optional[dict] = None

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
