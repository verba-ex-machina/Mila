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

    async def run(self) -> None:
        """Launch the Mila framework."""
        self.running = True
        while self.running:
            inbound_tasks: List[MilaTask] = []
            for handler in self.task_io_handlers:
                inbound_tasks.extend(await handler.recv())
            outbound_tasks: List[MilaTask] = []
            for task in inbound_tasks:
                if task.content == "exit":
                    self.running = False
                    break
                if not task.meta.destination:
                    task.meta.destination = task.meta.source.copy()
                outbound_tasks.append(task)
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
            for task in outbound_tasks:
                # Process tasks without a valid destination.
                print(f"Unroutable task: {task}")
            await asyncio.sleep(0.1)
