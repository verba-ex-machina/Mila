"""Define core functionality for Mila Framework assistants."""

from typing import Dict

from mila.base.types import MilaAssistant

ASSISTANTS: Dict[str, MilaAssistant] = {}


def get_assistants() -> dict:
    """Retrieve a list of available assistants."""
    return {
        name: assistant.description for name, assistant in ASSISTANTS.items()
    }


def register_assistant(assistant: MilaAssistant) -> None:
    """Register an assistant with the framework."""
    ASSISTANTS[assistant.name] = assistant
