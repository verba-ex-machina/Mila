"""Provide Mila Framework modules."""

import asyncio
from typing import List

from mila.assistants import ASSISTANTS
from mila.base.interfaces import TaskIO
from mila.base.types import MilaTask


class MilaIO(TaskIO):
    """Mila Framework I/O handler class."""

    async def recv(self) -> List[MilaTask]:
        """Retrieve responses from the assistants."""
        outbound: List[MilaTask] = []
        coros = [assistant.recv() for assistant in ASSISTANTS.values()]
        for coro in asyncio.as_completed(coros):
            try:
                outbound.extend(await coro)
            except asyncio.CancelledError:
                pass
        return outbound

    async def send(self, task_list: List[MilaTask]) -> None:
        """Send assigned tasks the assistants."""
        for task in task_list:
            if not task.assignee:
                task.assignee = "Overmind"
        # For now we're just dropping invalid tasks without notification.
        coros = [
            assistant.send(
                [task for task in task_list if task.assignee == assistant.name]
            )
            for assistant in ASSISTANTS.values()
        ]
        await asyncio.gather(*coros)
