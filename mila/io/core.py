"""Provide Mila Framework IO modules."""

import asyncio
from typing import List

from mila.assistant.util import assistant_list
from mila.base.collections import COMMANDS
from mila.base.interfaces import MilaLLM, TaskIO
from mila.base.types import AssistantDefinition, MilaTask


class CoreIO(TaskIO):
    """Mila Framework Core I/O handler class."""

    _bypass: List[MilaTask] = []
    _llm: MilaLLM = None

    def __init__(self, llm: MilaLLM) -> None:
        """Initialize the Core I/O handler."""
        self._llm = llm

    async def _recv_from(
        self, definition: AssistantDefinition
    ) -> List[MilaTask]:
        """Receive tasks from a single assistant."""
        assistant = await self._llm.get_assistant(definition)
        return await assistant.recv()

    async def recv(self) -> List[MilaTask]:
        """Retrieve responses from the assistants."""
        outbound: List[MilaTask] = []
        coros = [
            self._recv_from(definition) for definition in assistant_list()
        ]
        for coro in asyncio.as_completed(coros):
            try:
                outbound.extend(await coro)
            except asyncio.CancelledError:
                pass
        if self._bypass:
            outbound.extend(self._bypass)
            self._bypass = []
        return outbound

    async def _send_to(
        self, definition: AssistantDefinition, task_list: List[MilaTask]
    ) -> None:
        """Send tasks to a single assistant."""
        assistant = await self._llm.get_assistant(definition)
        await assistant.send(task_list)

    async def send(self, task_list: List[MilaTask]) -> None:
        """Send assigned tasks the assistants."""
        for task in task_list:
            if task in COMMANDS:
                self._bypass.append(task)
            elif not task.meta.assignment:
                task.meta.assignment = "Mila"
        # For now we're just dropping invalid tasks without notification.
        coros = [
            self._send_to(
                definition,
                [
                    task
                    for task in task_list
                    if task.meta.assignment == definition.name
                ],
            )
            for definition in assistant_list()
        ]
        await asyncio.gather(*coros)
