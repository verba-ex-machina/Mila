"""Define utility functions for Mila Framework assistants."""

from typing import List

from mila.base.collections import ASSISTANTS
from mila.base.types import AssistantDefinition


def assistant_list() -> List[AssistantDefinition]:
    """Retrieve all registered AssistantBase objects."""
    return ASSISTANTS.values()


async def assistant_dict() -> dict:
    """Retrieve the assistant registry as a dict."""
    return {
        name: assistant.description for name, assistant in ASSISTANTS.items()
    }


def register_assistant(assistant: AssistantDefinition) -> None:
    """Register an assistant with the framework."""
    ASSISTANTS[assistant.name] = assistant
