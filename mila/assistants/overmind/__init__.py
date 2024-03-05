"""Provide the Overmind Assistant for the Mila framework."""

from mila.assistants.core import register_assistant
from mila.base.types import MilaAssistant

register_assistant(
    MilaAssistant(
        name="Overmind",
        instructions=("You are Mila, a friendly assistant."),
        tools=[],
        model="gpt-3.5-turbo-1106",
        metadata={},
    )
)
