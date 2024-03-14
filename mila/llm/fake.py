"""Provide a FakeLLM implementation."""

from mila.base.interfaces import MilaAssistant
from mila.base.types import AssistantDefinition


class FakeLLM:
    """Fake LLM implementation."""

    # pylint: disable=too-few-public-methods

    def get_assistant(self, definition: AssistantDefinition):
        """Return a fake assistant."""
        return MilaAssistant(definition)
