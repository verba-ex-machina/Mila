"""Define essential data types for Mila."""

import dataclasses
import datetime
import hashlib
import json
from typing import Any, Dict, List, Optional, Union


@dataclasses.dataclass
class MilaTask:
    """Define a Mila task."""

    context: str
    prompt: str
    meta: Optional[dict] = None
    timestamp: Optional[str] = None  # ISO format (YYYY-MM-DDTHH:MM:SS.ffffffZ)
    id: Optional[str] = None

    def validate(self) -> None:
        """Validate the timestamp."""
        datetime.datetime.fromisoformat(self.timestamp)

    def _set_defaults(self) -> None:
        """Set default values for the task."""
        self.meta = self.meta or {}
        self.timestamp = self.timestamp or str(datetime.datetime.now())
        self.validate()
        self.id = (
            self.id
            or hashlib.sha256(json.dumps(self._dict).encode()).hexdigest()
        )

    @property
    def _dict(self) -> dict:
        """Return the task as a dictionary."""
        return dataclasses.asdict(self)

    def __repr__(self) -> str:
        """Return the string representation of the task."""
        self._set_defaults()
        return json.dumps(self._dict)

    def __hash__(self) -> int:
        """Return the hash of the task ID."""
        self._set_defaults()
        return hash(self.id)

    def __eq__(self, __value: object) -> bool:
        """Check if two tasks are equal."""
        return hash(self) == hash(__value)

    def __ne__(self, __value: object) -> bool:
        """Check if two tasks are not equal."""
        return hash(self) != hash(__value)

    def __lt__(self, __value: object) -> bool:
        """Check if the task is less than another task."""
        return hash(self) < hash(__value)

    def __le__(self, __value: object) -> bool:
        """Check if the task is less than or equal to another task."""
        return hash(self) <= hash(__value)

    def __gt__(self, __value: object) -> bool:
        """Check if the task is greater than another task."""
        return hash(self) > hash(__value)

    def __ge__(self, __value: object) -> bool:
        """Check if the task is greater than or equal to another task."""
        return hash(self) >= hash(__value)

    def __str__(self) -> str:
        """Return the string representation of the task."""
        return self.__repr__()

    def __bytes__(self) -> bytes:
        """Return the bytes representation of the task."""
        return self.__repr__().encode()

    def __iter__(self) -> list:
        """Return the task as an iterable."""
        self._set_defaults()
        for key, value in self._dict.items():
            yield key, value

    def __len__(self) -> int:
        """Return the length of the task."""
        return len(self.__repr__())
