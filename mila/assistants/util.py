"""Define utility functions for Mila Framework assistants."""

from mila.base.collections import ASSISTANTS
from mila.base.interfaces import AssistantBase
from mila.base.types import MilaAssistant


async def get_assistants() -> dict:
    """Retrieve a list of available assistants."""
    return {
        name: assistant.meta.description
        for name, assistant in ASSISTANTS.items()
    }


def register_assistant(assistant: MilaAssistant) -> None:
    """Register an assistant with the framework."""
    ASSISTANTS[assistant.name] = AssistantBase(assistant)
