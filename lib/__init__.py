"""Provide the Mila library."""

from lib.communication import Communication
from lib.connections import Connections
from lib.consciousness import Consciousness

class Mila:
    """Represent Mila."""

    def __init__(self):
        """Initialize Mila."""
        self._connections = Connections()
        self._consciousness = Consciousness()
        self._communication = Communication()
