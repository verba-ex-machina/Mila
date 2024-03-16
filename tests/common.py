"""Provide common functions across tests."""

from mila.base.types import (
    AssistantDefinition,
    MilaTask,
    MilaTool,
    ToolProperty,
)


async def _aprint(content: str) -> None:
    """Print content."""
    print(content)


def make_tool() -> MilaTool:
    """Make a MilaTool."""
    tool = MilaTool(
        name="print",
        function=_aprint,
        properties={
            "content": ToolProperty(
                type="string", description="Content to print."
            )
        },
        required=["content"],
    )
    return tool


def make_assistant() -> AssistantDefinition:
    """Make an AssistantDefinition."""
    assistant = AssistantDefinition(
        name="test assistant",
        description="test assistant description",
        instructions="test assistant instructions",
        tools=[make_tool()],
        model="gpt-3.5-turbo",
        metadata={},
    )
    return assistant


def make_task(data: str = "None") -> MilaTask:
    """Make a MilaTask."""
    task = MilaTask(context="context", content=data)
    return task
