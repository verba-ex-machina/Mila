"""Define core Assistants for the Mila framework."""

from typing import List

from mila.base.types import MilaAssistant

ASSISTANTS: List[MilaAssistant] = []


def get_assistants() -> dict:
    """Retrieve the list of available assistants."""
    return {assistant.name: assistant.description for assistant in ASSISTANTS}


def register_assistant(assistant: MilaAssistant) -> None:
    """Register an assistant with the Mila framework."""
    ASSISTANTS.append(assistant)
