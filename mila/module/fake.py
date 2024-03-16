"""Provide the Fake module."""

from mila.assistant.fake import FakeAssistant
from mila.base.interfaces import MilaAssistant, MilaLLM
from mila.base.types import AssistantDefinition


class FakeLLM(MilaLLM):
    """Fake LLM implementation."""

    async def get_assistant(
        self, definition: AssistantDefinition
    ) -> MilaAssistant:
        """Return a fake assistant."""
        return FakeAssistant(definition)

    async def setup(self) -> None:
        """Prepare the LLM."""

    async def teardown(self) -> None:
        """Teardown the LLM."""
