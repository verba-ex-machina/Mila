"""Provide Mila Framework OpenAI LLM integration."""

from openai import AsyncOpenAI

from mila.assistant.fake import FakeAssistant
from mila.base.interfaces import MilaAssistant, MilaLLM
from mila.base.types import AssistantDefinition


class OpenAILLM(MilaLLM):
    """Mila Framework OpenAI LLM class."""

    # pylint: disable=too-few-public-methods

    _llm: AsyncOpenAI = None

    def __init__(self) -> None:
        """Initialize the OpenAI LLM."""
        self._llm = AsyncOpenAI()

    async def get_assistant(
        self, definition: AssistantDefinition
    ) -> MilaAssistant:
        """Return an assistant for the given definition."""
        return FakeAssistant(definition)
