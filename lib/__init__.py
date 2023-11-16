"""Provide the Mila library."""

from lib.consciousness import Consciousness


class Mila:
    """Represent Mila."""

    def __init__(self):
        """Initialize Mila."""
        self._consciousness = Consciousness()
        self.prompt = self._consciousness.prompt
