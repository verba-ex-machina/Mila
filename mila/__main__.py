"""Execute the Mila framework as an all-in-one module."""

import asyncio
from typing import List

from .base.interfaces import TaskIO
from .base.types import MilaTask
from .module.discord import DiscordIO


async def main() -> None:
    """Execute the Mila framework."""
    task_io_handlers: List[TaskIO] = [
        DiscordIO(),
    ]
    for handler in task_io_handlers:
        await handler.setup()
    running = True
    while running:
        inbound_tasks: List[MilaTask] = []
        outbound_tasks: List[MilaTask] = []
        # Receive inbound tasks.
        for handler in task_io_handlers:
            tasks = await handler.recv()
            for task in tasks:
                task.meta.source["handler"] = handler.NAME
                inbound_tasks.append(task)
        # Process inbound_tasks.
        for task in inbound_tasks:
            if task.content == "exit":
                running = False
                break
            task.meta.destination = task.meta.source.copy()
            outbound_tasks.append(task)
        # Send outbound tasks.
        for handler in task_io_handlers:
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
        await asyncio.sleep(0.1)

    for handler in task_io_handlers:
        await handler.teardown()


if __name__ == "__main__":
    asyncio.run(main())
