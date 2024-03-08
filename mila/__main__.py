"""Execute the Mila Framework as an all-in-one module."""

import asyncio
from typing import List

from mila import MilaProc
from mila.base.interfaces import TaskIO
from mila.module.db import SqliteDB
from mila.module.discord import DiscordIO

TASK_IO_HANDLERS: List[TaskIO] = [DiscordIO]


async def main():
    """Launch the Mila Framework."""
    async with SqliteDB() as sqlite:
        async with MilaProc(
            db=sqlite,
            task_io_handlers=TASK_IO_HANDLERS,
        ) as mila:
            await mila.run()


if __name__ == "__main__":
    asyncio.run(main())
