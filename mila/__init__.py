"""Provide the Mila framework."""

import asyncio
from typing import List

from .base.interfaces import TaskIO
from .base.types import MilaTask


class Mila:
    """Mila framework class."""

    # pylint: disable=too-few-public-methods

    def __init__(self, task_io_handlers: List[TaskIO]) -> None:
        """Initialize the Mila framework."""
        self.task_io_handlers: List[TaskIO] = [
            # Instantiate each handler.
            handler()
            for handler in task_io_handlers
        ]
        self.running = False

    async def __aenter__(self) -> "Mila":
        """Enter the Mila framework."""
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        """Exit the Mila framework."""

    async def _get_inbound_tasks(self) -> List[MilaTask]:
        """Get inbound tasks from their respective handlers."""
        inbound_tasks = []
        for handler in self.task_io_handlers:
            tasks = await handler.recv()
            for task in tasks:
                task.meta.source["handler"] = handler.NAME
                inbound_tasks.append(task)
        return inbound_tasks

    async def _main_loop(self):
        """Run the main loop of the Mila framework."""
        self.running = True
        while self.running:
            await self._send_outbound_tasks(
                await self._process_tasks(await self._get_inbound_tasks())
            )
            await asyncio.sleep(0.1)

    async def _process_tasks(
        self, inbound_tasks: List[MilaTask]
    ) -> List[MilaTask]:
        """Process inbound tasks and return outbound tasks."""
        outbound_tasks = []
        for task in inbound_tasks:
            if task.content == "exit":
                self.running = False
                break
            if not task.meta.destination:
                # Echo server.
                task.meta.destination = task.meta.source.copy()
            outbound_tasks.append(task)
        return outbound_tasks

    async def _send_outbound_tasks(
        self, outbound_tasks: List[MilaTask]
    ) -> None:
        """Send outbound tasks to their respective handlers."""
        for handler in self.task_io_handlers:
            tasks = [
                task
                for task in outbound_tasks
                if task.meta.destination["handler"] == handler.NAME
            ]
            outbound_tasks = [
                task
                for task in outbound_tasks
                if task.meta.destination["handler"] != handler.NAME
            ]
            for task in tasks:
                await handler.send(task)

    async def _setup(self):
        """Set up the Mila framework."""
        for handler in self.task_io_handlers:
            await handler.setup()

    async def _teardown(self):
        """Tear down the Mila framework."""
        for handler in self.task_io_handlers:
            await handler.teardown()

    async def run(self) -> None:
        """Launch the Mila framework."""
        await self._setup()
        await self._main_loop()
        await self._teardown()
