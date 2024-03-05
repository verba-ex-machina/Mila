"""Define core Assistants for the Mila framework."""

from mila.base.types import MilaAssistant

ASSISTANTS = []


def register_assistant(assistant):
    """Register an assistant with the Mila framework."""
    ASSISTANTS.append(assistant)


register_assistant(
    MilaAssistant(
        name="Overmind",
        instructions=("You are Mila, a friendly assistant."),
        tools=[],
        model="gpt-3.5-turbo-1106",
        metadata={},
    )
)
