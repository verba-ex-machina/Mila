"""Provide Mila Framework OpenAI LLM integration."""

from typing import List

from openai import AsyncOpenAI
from openai.types.beta.assistant import Assistant

from mila.base.interfaces import MilaAssistant, MilaLLM, MilaTask
from mila.base.types import AssistantDefinition


class OpenAIAssistant(MilaAssistant):
    """Mila Framework OpenAI Assistant class."""

    _llm: AsyncOpenAI = None
    _assistant: Assistant = None

    def __init__(
        self, assistant: AssistantDefinition, llm: AsyncOpenAI
    ) -> None:
        """Initialize the OpenAI assistant."""
        super().__init__(assistant)
        self._llm = llm

    @staticmethod
    def _requires_assistant(function: callable) -> callable:
        """Require an assistant to be set."""

        async def wrapper(self: "OpenAIAssistant", *args, **kwargs):
            # pylint: disable=protected-access
            if not self._assistant:
                await self.setup()
            return await function(self, *args, **kwargs)

        return wrapper

    async def setup(self) -> None:
        """Set up the assistant."""
        assistant_list = await self._llm.beta.assistants.list(limit=100)
        for assistant in assistant_list.data:
            if assistant.name == self.meta.name:
                if (
                    "hash" not in assistant.metadata.keys()
                    or assistant.metadata["hash"] != hash(self.meta)
                ):
                    await self._llm.beta.assistants.update(
                        assistant_id=assistant.id,
                        name=self.meta.name,
                        description=self.meta.description,
                        instructions=self.meta.instructions,
                        tools=[tool.definition for tool in self.meta.tools],
                        model=self.meta.model,
                        metadata=self.meta.metadata,
                    )
                self._assistant = assistant
                return
        self._assistant = await self._llm.beta.assistants.create(
            name=self.meta.name,
            description=self.meta.description,
            instructions=self.meta.instructions,
            tools=[tool.definition for tool in self.meta.tools],
            model=self.meta.model,
            metadata=self.meta.metadata,
        )

    @_requires_assistant
    async def recv(self) -> List[MilaTask]:
        """Receive tasks from the assistant."""
        raise NotImplementedError

    @_requires_assistant
    async def send(self, task_list: List[MilaTask]) -> None:
        """Send tasks to the assistant."""
        raise NotImplementedError


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
        return OpenAIAssistant(definition, self._llm)
