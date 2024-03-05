"""Provide the Overmind Assistant for the Mila framework."""

from mila.assistants.core import get_assistants, register_assistant
from mila.base.types import MilaAssistant, MilaTool

OVERMIND_TOOLS = [
    MilaTool(
        name="get_assistants",
        description=get_assistants.__doc__,
        function=get_assistants,
        properties={},
        required=[],
    )
]

register_assistant(
    MilaAssistant(
        name="Overmind",
        description="The orchestrator of the Mila framework.",
        instructions=("You are Mila, a friendly assistant."),
        tools=OVERMIND_TOOLS,
        model="gpt-3.5-turbo-1106",
        metadata={},
    )
)
