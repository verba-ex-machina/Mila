"""Execute the Mila framework as an all-in-one module."""

import asyncio
from typing import List

from .base.interfaces import TaskIO
from .base.types import MilaTask
from .module.discord import DiscordIO


class Mila:
    """Mila framework class."""

    def __init__(self):
        """Initialize the Mila framework."""
        self.task_io_handlers: List[TaskIO] = [
            DiscordIO(),
        ]
        self.running = False

    async def _main(self) -> None:
        """Execute the Mila framework."""
        for handler in self.task_io_handlers:
            await handler.setup()
        self.running = True
        while self.running:
            await self.send_outbound_tasks(
                await self.process_tasks(await self.get_inbound_tasks())
            )
            await asyncio.sleep(0.1)

        for handler in self.task_io_handlers:
            await handler.teardown()

    async def send_outbound_tasks(self, outbound_tasks):
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

    async def process_tasks(self, inbound_tasks: List[MilaTask]):
        """Process inbound tasks and return outbound tasks."""
        outbound_tasks: List[MilaTask] = []
        for task in inbound_tasks:
            if task.content == "exit":
                self.running = False
                break
            task.meta.destination = task.meta.source.copy()
            outbound_tasks.append(task)
        return outbound_tasks

    async def get_inbound_tasks(self):
        """Get inbound tasks from their respective handlers."""
        inbound_tasks: List[MilaTask] = []
        for handler in self.task_io_handlers:
            tasks = await handler.recv()
            for task in tasks:
                task.meta.source["handler"] = handler.NAME
                inbound_tasks.append(task)
        return inbound_tasks

    def start(self):
        """Start the Mila framework."""
        asyncio.run(self._main())


if __name__ == "__main__":
    Mila().start()
