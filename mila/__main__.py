"""Execute the Mila framework as an all-in-one module."""

import asyncio
from typing import List

from .base.interfaces import TaskIO
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
        for handler in task_io_handlers:
            tasks = await handler.recv()
            for task in tasks:
                task.meta.source["handler"] = handler.NAME
                if task.content == "exit":
                    running = False
                    break
                print(task)
        await asyncio.sleep(1)

    for handler in task_io_handlers:
        await handler.teardown()


if __name__ == "__main__":
    asyncio.run(main())
