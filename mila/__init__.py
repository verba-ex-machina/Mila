"""Provide the Mila library."""

import openai

from mila.assistants import Assistant
from mila.logging import logging
from mila.prompts import PROMPTS
from mila.runs import Run
from mila.threads import Thread


class Mila:
    """Represent the Mila assistant."""

    def __init__(self, logger: logging.Logger):
        """Initialize Mila."""
        self._llm = openai.AsyncOpenAI()
        self._logger = logger
        self._assistant = Assistant(llm=self._llm, logger=self._logger)
        self._threads = {}
        self._runs = {}

    async def check_completion(self, thread_id: str) -> bool:
        """Check whether a query run is complete."""
        return await self._runs[thread_id].check()

    async def get_response(self, thread_id: str) -> str:
        """Retrieve the final response from a given run."""
        return await self._runs[thread_id].response()

    async def handle_message(
        self,
        author: str,
        name: str,
        query: str,
        context: str,
    ) -> str:
        """Handle an incoming message."""
        self._logger.info(
            "Message received from %s (%s): %s",
            author,
            name,
            query,
        )
        new_thread = Thread(llm=self._llm)
        thread_id = await new_thread.id()
        if author not in self._threads:
            self._threads[author] = [new_thread]
        else:
            self._threads[author].append(new_thread)
        await self._llm.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=PROMPTS.format(
                name="user",
                sub_dict={
                    "context": context,
                    "query": query,
                },
            ),
        )
        new_run = Run(
            llm=self._llm,
            logger=self._logger,
            thread_id=thread_id,
            assistant_id=await self._assistant.id(),
        )
        self._runs[thread_id] = new_run
        return thread_id
