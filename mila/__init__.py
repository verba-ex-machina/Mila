"""Provide the Mila library."""

from mila.consciousness import Consciousness
from mila.constants import DESCRIPTION


class Mila:
    """Represent Mila."""

    description = DESCRIPTION

    def __init__(self):
        """Initialize Mila."""
        self._consciousness = Consciousness()
        self.prompt = self._consciousness.prompt


MILA = Mila()
