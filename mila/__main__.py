"""Execute the Mila Framework as an all-in-one module."""

from typing import List

import mila
from mila.base.interfaces import TaskIO
from mila.modules.discord import DiscordIO
from mila.modules.fake import FakeTracker
from mila.modules.openai import OpenAILLM

TASK_IO_HANDLERS: List[TaskIO] = [DiscordIO]

if __name__ == "__main__":
    mila.run(
        llm=OpenAILLM,
        task_io_handlers=[DiscordIO],
        task_tracker=FakeTracker,
    )
