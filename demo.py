#!/usr/bin/env python3

"""Provide a Mila Framework demonstration script."""

import asyncio
import signal
import sys

from mila import MilaProc
from mila.base.types import AssistantDefinition, MilaTool, ToolProperty
from mila.base.util import register_assistant
from mila.modules.discord import DiscordIO
from mila.modules.openai import OpenAILLM


async def echo(text: str) -> str:
    """Return the input text...backwards."""
    return text[::-1]


echo_assistant = AssistantDefinition(
    name="Echo",
    description="Echo Assistant",
    instructions="""
    Act as an echo bot. Any text you receive, run it through the 'echo' tool,
    then return the result.
    """,
    tools=[
        MilaTool(
            name="echo",
            function=echo,
            properties=[
                ToolProperty(
                    name="text",
                    type="string",
                    description="The text to be echoed.",
                )
            ],
            required=["text"],
        )
    ],
    model="gpt-3.5-turbo-1106",
)

register_assistant(echo_assistant)


def sigint_handler(signum, frame):
    """Handle SIGINT."""
    # pylint: disable=unused-argument
    sys.exit(0)


async def main():
    """Launch the Mila Framework."""
    signal.signal(signal.SIGINT, sigint_handler)
    async with OpenAILLM() as llm:
        async with MilaProc(llm=llm, task_io_handlers=[DiscordIO]) as mila:
            await mila.run()


if __name__ == "__main__":
    asyncio.run(main())
