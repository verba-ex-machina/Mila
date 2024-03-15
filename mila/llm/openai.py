"""Provide Mila Framework OpenAI LLM integration."""

from typing import List

from openai import AsyncOpenAI
from openai.types.beta.assistant import Assistant

from mila.base.interfaces import MilaAssistant, MilaLLM, MilaTask
from mila.base.types import AssistantDefinition


class OpenAIAssistant(MilaAssistant):
    """Mila Framework OpenAI Assistant class."""

    _llm: "OpenAILLM" = None
    _assistant: Assistant = None

    def __init__(self, definition: AssistantDefinition, llm: MilaLLM) -> None:
        """Initialize the OpenAI assistant."""
        super().__init__(definition)
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
        for assistant in await self._llm.oai_assistant_list():
            if assistant.name == self.meta.name:
                if (
                    "hash" not in assistant.metadata.keys()
                    or assistant.metadata["hash"] != hash(self.meta)
                ):
                    self._assistant = await self._llm.oai_assistant_update(
                        assistant.id, self.meta
                    )
                    return
                self._assistant = assistant
        self._assistant = await self._llm.oai_assistant_create(self.meta)

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

    _llm: AsyncOpenAI = None

    def __init__(self) -> None:
        """Initialize the OpenAI LLM."""
        self._llm = AsyncOpenAI()

    async def get_assistant(
        self, definition: AssistantDefinition
    ) -> MilaAssistant:
        """Return an assistant for the given definition."""
        return OpenAIAssistant(definition=definition, llm=self)

    async def oai_assistant_update(
        self, assistant_id: str, definition: AssistantDefinition
    ) -> None:
        """Update the specified OpenAI assistant."""
        return await self._llm.beta.assistants.update(
            assistant_id=assistant_id,
            name=definition.name,
            description=definition.description,
            instructions=definition.instructions,
            tools=[tool.definition for tool in definition.tools],
            model=definition.model,
            metadata={
                "hash": hash(definition),
                **definition.metadata,
            },
        )

    async def oai_assistant_create(
        self, definition: AssistantDefinition
    ) -> Assistant:
        """Create a new OpenAI assistant."""
        return await self._llm.beta.assistants.create(
            name=definition.name,
            description=definition.description,
            instructions=definition.instructions,
            tools=[tool.definition for tool in definition.tools],
            model=definition.model,
            metadata={
                "hash": hash(definition),
                **definition.metadata,
            },
        )

    async def oai_assistant_list(self) -> List[Assistant]:
        """List all OpenAI assistants."""
        response = await self._llm.beta.assistants.list(limit=100)
        return response.data

    async def oai_assistant_delete(self, assistant_id: str) -> None:
        """Delete the specified OpenAI assistant."""
        await self._llm.beta.assistants.delete(assistant_id)

    async def teardown(self) -> None:
        """Perform OpenAI LLM teardown."""
        for assistant in await self.oai_assistant_list():
            # Don't delete assistants that aren't part of Mila.
            # All of ours use the "hash" metadata key.
            # This isn't a perfect solution, but it'll do for now.
            if "hash" in assistant.metadata.keys():
                await self.oai_assistant_delete(assistant.id)
