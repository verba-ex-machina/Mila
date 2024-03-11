"""Provide Mila Framework modules."""

import asyncio
from typing import List

from mila.assistants import ASSISTANTS
from mila.base.commands import COMMANDS
from mila.base.interfaces import TaskIO
from mila.base.types import MilaTask


class MilaIO(TaskIO):
    """Mila Framework I/O handler class."""

    _bypass: List[MilaTask] = []

    async def recv(self) -> List[MilaTask]:
        """Retrieve responses from the assistants."""
        outbound: List[MilaTask] = []
        coros = [assistant.recv() for assistant in ASSISTANTS.values()]
        for coro in asyncio.as_completed(coros):
            try:
                outbound.extend(await coro)
            except asyncio.CancelledError:
                pass
        if self._bypass:
            outbound.extend(self._bypass)
            self._bypass = []
        return outbound

    async def send(self, task_list: List[MilaTask]) -> None:
        """Send assigned tasks the assistants."""
        for task in task_list:
            if task in COMMANDS:
                self._bypass.append(task)
            elif not task.meta.assignment:
                task.meta.assignment = "Overmind"
        # For now we're just dropping invalid tasks without notification.
        coros = [
            assistant.send(
                [
                    task
                    for task in task_list
                    if task.meta.assignment == assistant.name
                ]
            )
            for assistant in ASSISTANTS.values()
        ]
        await asyncio.gather(*coros)
