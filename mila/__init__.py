"""Provide the Mila Framework."""

import asyncio
from typing import List

from mila.base.collections import COMMANDS
from mila.base.commands import POWER_WORD_KILL
from mila.base.constants import STATES, TICK
from mila.base.interfaces import MilaLLM, TaskIO
from mila.base.types import MilaTask
from mila.module.core import CoreIO


class MilaProc:
    """Mila Framework process class."""

    _llm: MilaLLM
    _task_io_handlers: List[TaskIO]

    def __init__(self, llm: MilaLLM, task_io_handlers: List[TaskIO]) -> None:
        """Initialize the Mila Framework."""
        self._llm = llm
        self._task_io_handlers = [
            CoreIO(llm=self._llm),
        ]
        self._task_io_handlers.extend(
            [handler() for handler in task_io_handlers]
        )
        self.running = False

    async def __aenter__(self) -> "MilaProc":
        """Set up the Mila Framework."""
        await asyncio.gather(
            *[handler.setup() for handler in self._task_io_handlers]
        )
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        """Tear down the Mila Framework."""
        await asyncio.gather(
            *[handler.teardown() for handler in self._task_io_handlers]
        )

    async def _collect_tasks_from(self, handler: TaskIO) -> List[MilaTask]:
        """Collect inbound tasks from a single handler."""
        task_list = await handler.recv()
        for task in task_list:
            if task not in COMMANDS:
                task.src.handler = handler.__class__.__name__
        return task_list

    async def _collect_inbound_tasks(
        self, tasks: List[MilaTask]
    ) -> List[MilaTask]:
        """Collect all inbound tasks from all handlers."""
        for task_list in await asyncio.gather(
            *[
                self._collect_tasks_from(handler)
                for handler in self._task_io_handlers
            ]
        ):
            tasks.extend(task_list)
        return tasks

    async def _process_task(self, task: MilaTask) -> MilaTask:
        """Process a single task."""
        if task == POWER_WORD_KILL:
            self.running = False
        elif not task.dst.handler:
            task.dst.handler = CoreIO.__name__
        return task

    async def _process_tasks(self, tasks: List[MilaTask]) -> List[MilaTask]:
        """Process inbound tasks. Return outbound tasks."""
        return [
            task
            for task in await asyncio.gather(
                *[self._process_task(task) for task in tasks]
            )
            if task.meta.state != STATES.COMPLETE
        ]

    async def _route_outbound_tasks(
        self, tasks: List[MilaTask]
    ) -> List[MilaTask]:
        """Send outbound tasks to their respective handlers."""
        await asyncio.gather(
            *[
                handler.send(
                    [
                        task
                        for task in tasks
                        if task in COMMANDS
                        or task.dst.handler == handler.__class__.__name__
                    ]
                )
                for handler in self._task_io_handlers
            ]
        )
        return [
            task
            for task in tasks
            if task not in COMMANDS
            and task.dst.handler
            not in [
                handler.__class__.__name__
                for handler in self._task_io_handlers
            ]
        ]

    async def _handle_unprocessed_tasks(
        self, tasks: List[MilaTask]
    ) -> List[MilaTask]:
        for task in tasks:
            print(f"Unroutable task: {task}")
            task.meta.state = STATES.COMPLETE
        return tasks

    async def run(self) -> None:
        """Launch the Mila Framework."""
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
            await asyncio.sleep(TICK)
