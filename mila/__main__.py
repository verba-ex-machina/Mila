"""Execute the Mila Framework as an all-in-one module."""

import asyncio
from typing import List

from mila import MilaProc
from mila.base.interfaces import MilaLLM, TaskIO
from mila.io.discord import DiscordIO
from mila.llm.fake import FakeLLM

TASK_IO_HANDLERS: List[TaskIO] = [DiscordIO]
LLM_BACKEND: MilaLLM = FakeLLM


async def main():
    """Launch the Mila Framework."""
    async with MilaProc(
        llm=LLM_BACKEND, task_io_handlers=TASK_IO_HANDLERS
    ) as mila:
        await mila.run()


if __name__ == "__main__":
    asyncio.run(main())
