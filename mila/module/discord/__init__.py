"""Provide Discord modules for Mila."""

from typing import Union

from mila.base.interfaces import TaskIO
from mila.base.types import MilaTask

class DiscordIO(TaskIO):
    """Implement a Discord TaskIO adapter."""

    def __init__(self) -> None:
        """Initialize the DiscordIO."""
        pass

    async def recv(self) -> Union[MilaTask, None]:
        """Receive a task from Discord."""
        pass

    async def send(self, task: MilaTask) -> None:
        """Send a task to Discord."""
        pass