"""Provide the Mila framework."""

import asyncio
from typing import List

from .base.interfaces import TaskIO
from .base.types import MilaTask


class MilaProc:
    """Mila framework process class."""

    # pylint: disable=too-few-public-methods

    def __init__(self, task_io_handlers: List[TaskIO]) -> None:
        """Initialize the Mila framework."""
        self.task_io_handlers: List[TaskIO] = [
            # Instantiate each handler.
            handler()
            for handler in task_io_handlers
        ]
        self.running = False

    async def __aenter__(self) -> "MilaProc":
        """Set up the Mila framework."""
        for handler in self.task_io_handlers:
            await handler.setup()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        """Tear down the Mila framework."""
        for handler in self.task_io_handlers:
            await handler.teardown()

    async def _collect_inbound_tasks(
        self, inbound_tasks: List[MilaTask]
    ) -> List[MilaTask]:
        """Collect all inbound tasks from all handlers."""
        for task_list in await asyncio.gather(
            *[handler.recv() for handler in self.task_io_handlers]
        ):
            inbound_tasks.extend(task_list)
        return inbound_tasks

    async def _handle_unprocessed_tasks(
        self, unhandled_tasks: List[MilaTask]
    ) -> List[MilaTask]:
        for task in unhandled_tasks:
            # Process tasks without a valid destination.
            print(f"Unroutable task: {task}")
            task.meta.state = "complete"
        return unhandled_tasks

    async def _process_task(self, task: MilaTask) -> MilaTask:
        """Process a single task."""
        if task.content == "exit":
            self.running = False
            task.meta.state = "complete"
        if not task.meta.destination:
            # Default to the FakeIO handler, an echo server.
            task.meta.destination["handler"] = "FakeIO"
        return task

    async def _process_tasks(
        self, inbound_tasks: List[MilaTask]
    ) -> List[MilaTask]:
        """Process inbound tasks. Return outbound tasks."""
        return [
            task
            for task in await asyncio.gather(
                *[self._process_task(task) for task in inbound_tasks]
            )
            # Filter out tasks that are deemed complete.
            if task.meta.state != "complete"
        ]

    async def _route_outbound_tasks(
        self, outbound_tasks: List[MilaTask]
    ) -> List[MilaTask]:
        """Send outbound tasks to their respective handlers."""
        await asyncio.gather(
            *[
                handler.send(
                    [
                        task
                        for task in outbound_tasks
                        if task.meta.destination["handler"] == handler.NAME
                    ]
                )
                for handler in self.task_io_handlers
            ]
        )
        return [
            # Unhandled tasks.
            task
            for task in outbound_tasks
            if task.meta.destination["handler"]
            not in [handler.NAME for handler in self.task_io_handlers]
        ]

    async def run(self) -> None:
        """Launch the Mila framework."""
        self.running = True
        pipeline = [
            self._collect_inbound_tasks,
            self._process_tasks,
            self._route_outbound_tasks,
            self._handle_unprocessed_tasks,
        ]
        task_list = []
        while self.running:
            for step in pipeline:
                task_list = await step(task_list)
            await asyncio.sleep(0.1)
