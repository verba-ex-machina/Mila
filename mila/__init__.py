"""Provide the Mila library."""

from mila.assistants import Assistant
from mila.logging import LOGGER
from mila.threads import Thread


class Mila:
    """Represent the Mila assistant."""

    def __init__(self):
        """Initialize Mila."""
        self._assistant = Assistant()
        self._threads = {}

    async def check_completion(self, thread_id: str) -> bool:
        """Check whether a query run is complete."""
        return await self._threads[thread_id].check()

    async def get_response(self, thread_id: str) -> str:
        """Retrieve the final response from a given run."""
        return await self._threads[thread_id].response()

    async def handle_message(
        self,
        author: str,
        name: str,
        query: str,
        context: str,
    ) -> str:
        """Handle an incoming message."""
        LOGGER.info(
            "Message received from %s (%s): %s",
            author,
            name,
            query,
        )
        new_thread = Thread(
            assistant_id=await self._assistant.id(),
            context=context,
            query=query,
        )
        thread_id = await new_thread.id()
        self._threads[thread_id] = new_thread
        return thread_id
