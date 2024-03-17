#!/usr/bin/env python3

"""Provide a Mila Framework demonstration script."""

import mila
from mila.base.types import AssistantDefinition, MilaTool, ToolProperty
from mila.base.util import register_assistant
from mila.modules.discord import DiscordIO
from mila.modules.fake import FakeTracker
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


if __name__ == "__main__":
    mila.run(
        llm=OpenAILLM, task_io_handlers=[DiscordIO], task_tracker=FakeTracker
    )
