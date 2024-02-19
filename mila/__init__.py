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

    def _handle_unprocessed_tasks(
        self, unhandled_tasks: List[MilaTask]
    ) -> None:
        for task in unhandled_tasks:
            # Process tasks without a valid destination.
            print(f"Unroutable task: {task}")

    def _process_tasks(self, task_list: List[MilaTask]) -> List[MilaTask]:
        """Process inbound tasks."""
        if any(task.content == "exit" for task in task_list):
            self.running = False
            return []
        for task in task_list:
            # Echo server: send the task back to the source.
            task.meta.destination = (
                task.meta.destination or task.meta.source.copy()
            )
        return task_list

    async def _route_outbound_tasks(
        self, outbound_tasks: List[MilaTask]
    ) -> List[MilaTask]:
        """Send outbound tasks to their respective handlers."""
        for handler in self.task_io_handlers:
            await handler.send(
                [
                    task
                    for task in outbound_tasks
                    if task.meta.destination["handler"] == handler.NAME
                ]
            )
            outbound_tasks = [
                task
                for task in outbound_tasks
                if task.meta.destination["handler"] != handler.NAME
            ]
        return outbound_tasks

    async def run(self) -> None:
        """Launch the Mila framework."""
        self.running = True
        while self.running:
            self._handle_unprocessed_tasks(
                await self._route_outbound_tasks(
                    self._process_tasks(await self._collect_inbound_tasks())
                )
            )
            await asyncio.sleep(0.1)
