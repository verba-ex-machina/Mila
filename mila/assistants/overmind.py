"""Provide the Overmind Assistant for the Mila Framework."""

from mila.assistants.core import get_assistants, register_assistant
from mila.base.types import MilaAssistant, MilaTool

OVERMIND_TOOLS = [
    MilaTool(
        name="get_assistants",
        function=get_assistants,
        properties={},
        required=[],
    )
]

register_assistant(
    MilaAssistant(
        name="Overmind",
        description="The orchestrator of the Mila Framework.",
        instructions=("You are Mila, a friendly assistant."),
        tools=OVERMIND_TOOLS,
        model="gpt-3.5-turbo-1106",
        metadata={},
    )
)
