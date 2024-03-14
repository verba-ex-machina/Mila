"""Provide common functions across tests."""

from mila.base.types import AssistantDefinition, MilaTask


def make_assistant() -> AssistantDefinition:
    """Make an AssistantDefinition."""
    assistant = AssistantDefinition(
        name="test assistant",
        description="test assistant description",
        instructions="test assistant instructions",
        tools=[],
        model="gpt-3.5-turbo",
        metadata={},
    )
    return assistant


def make_task(data: str = "None") -> MilaTask:
    """Make a MilaTask."""
    task = MilaTask(context="context", content=data)
    return task
