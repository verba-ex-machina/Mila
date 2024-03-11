"""Define utility functions for Mila Framework assistants."""

from typing import List

from mila.base.collections import ASSISTANTS
from mila.base.interfaces import AssistantBase
from mila.base.types import MilaAssistant


def assistant_list() -> List[AssistantBase]:
    """Retrieve all registered AssistantBase objects."""
    return ASSISTANTS.values()


async def assistant_dict() -> dict:
    """Retrieve the assistant registry as a dict."""
    return {
        name: assistant.meta.description
        for name, assistant in ASSISTANTS.items()
    }


def register_assistant(assistant: MilaAssistant) -> None:
    """Register an assistant with the framework."""
    ASSISTANTS[assistant.name] = AssistantBase(assistant)
