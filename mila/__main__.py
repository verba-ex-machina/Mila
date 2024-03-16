"""Execute the Mila Framework as an all-in-one module."""

import asyncio
import signal
import sys
from typing import List

from mila import MilaProc
from mila.base.interfaces import TaskIO
from mila.module.discord import DiscordIO
from mila.module.openai import OpenAILLM

TASK_IO_HANDLERS: List[TaskIO] = [DiscordIO]


def sigint_handler(signum, frame):
    """Handle SIGINT."""
    # pylint: disable=unused-argument
    sys.exit(0)


async def main():
    """Launch the Mila Framework."""
    signal.signal(signal.SIGINT, sigint_handler)
    async with OpenAILLM() as llm:
        async with MilaProc(
            llm=llm, task_io_handlers=TASK_IO_HANDLERS
        ) as mila:
            await mila.run()


if __name__ == "__main__":
    asyncio.run(main())
