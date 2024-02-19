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
        """Set up the Mila framework."""
        for handler in self.task_io_handlers:
            await handler.setup()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        """Tear down the Mila framework."""
        for handler in self.task_io_handlers:
            await handler.teardown()

    async def _collect_inbound_tasks(self) -> List[MilaTask]:
        """Collect all inbound tasks from all handlers."""
        inbound_tasks = []
        for handler in self.task_io_handlers:
            inbound_tasks.extend(await handler.recv())
        return inbound_tasks

    def _handle_unprocessed_tasks(self, unhandled_tasks):
        for task in unhandled_tasks:
            # Process tasks without a valid destination.
            print(f"Unroutable task: {task}")

    def _process_tasks(self, inbound_tasks: List[MilaTask]) -> List[MilaTask]:
        """Process inbound tasks."""
        outbound_tasks = []
        for task in inbound_tasks:
            if task.content == "exit":
                self.running = False
                break
            if not task.meta.destination:
                task.meta.destination = task.meta.source.copy()
            outbound_tasks.append(task)
        return outbound_tasks

    async def _send_outbound_tasks(self, outbound_tasks):
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
        return outbound_tasks

    async def run(self) -> None:
        """Launch the Mila framework."""
        self.running = True
        while self.running:
            inbound_tasks = await self._collect_inbound_tasks()
            outbound_tasks = self._process_tasks(inbound_tasks)
            unhandled_tasks = await self._send_outbound_tasks(outbound_tasks)
            self._handle_unprocessed_tasks(unhandled_tasks)
            await asyncio.sleep(0.1)
