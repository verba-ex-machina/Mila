"""Provide access to the OpenAI Threads feature."""

import openai


class Thread:
    """Provide an abstraction for the OpenAI Threads API."""

    def __init__(self, llm: openai.OpenAI):
        """Initialize the Thread."""
        self._llm = llm
        self._thread = None

    async def _spawn_thread(self):
        """Spawn a new thread."""
        self._thread = await self._llm.beta.threads.create(
            messages=[],
        )

    async def id(self) -> str:
        """Get the ID of the thread."""
        if not self._thread:
            await self._spawn_thread()
        return self._thread.id
