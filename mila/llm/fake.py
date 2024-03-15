"""Provide a FakeLLM implementation."""

from mila.assistant.fake import FakeAssistant
from mila.base.interfaces import MilaAssistant, MilaLLM
from mila.base.types import AssistantDefinition


class FakeLLM(MilaLLM):
    """Fake LLM implementation."""

    # pylint: disable=too-few-public-methods

    async def get_assistant(
        self, definition: AssistantDefinition
    ) -> MilaAssistant:
        """Return a fake assistant."""
        return FakeAssistant(definition)
