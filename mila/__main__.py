"""Execute the Mila Framework as an all-in-one module."""

import asyncio
from typing import List

from mila import MilaProc
from mila.base.interfaces import TaskIO
from mila.io.discord import DiscordIO

TASK_IO_HANDLERS: List[TaskIO] = [DiscordIO]


async def main():
    """Launch the Mila Framework."""
    async with MilaProc(task_io_handlers=TASK_IO_HANDLERS) as mila:
        await mila.run()


if __name__ == "__main__":
    asyncio.run(main())
