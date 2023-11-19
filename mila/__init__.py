"""Provide the Mila library."""

import logging
from hashlib import sha256
from typing import AsyncIterator

from mila.constants import DESCRIPTION
from mila.llm import LLM
from mila.prompts import PROMPTS


class Mila:
    """Represent Mila."""

    class MilaTask:
        """Represent a single request to the Mila AI."""

        def __init__(self, query: str, context: str, generator: AsyncIterator):
            """Initialize the task."""
            self.query = query
            self.context = context
            self.generator = generator
            self.response = ""

    def __init__(self, logger: logging.Logger):
        """Initialize Mila."""
        self.description = DESCRIPTION
        self._chain = PROMPTS | LLM
        self._logger = logger
        self._tasks = {}

    def add_task(self, query: str, context: str) -> str:
        """Add a task to Mila."""
        task_id = sha256((query + context).encode("utf-8")).hexdigest()
        self._logger.info("Task %s created. -> %s", task_id, query)
        generator = self._chain.astream(
            {
                "query": query,
                "context": context,
            }
        )
        self._tasks[task_id] = self.MilaTask(query, context, generator)
        return task_id

    async def check(self, task_id: str) -> bool:
        """Check whether the task is complete."""
        task = self._tasks[task_id]
        try:
            # Retrieve the next chunk of text.
            chunk = await task.generator.__anext__()
            task.response += chunk.content
        except StopAsyncIteration:
            self._logger.info("Task %s complete.", task_id)
            return True
        return False

    def drop_task(self, task_id: str) -> None:
        """Drop a task."""
        del self._tasks[task_id]

    def get_response(self, task_id: str) -> str:
        """Get the response to a task."""
        return self._tasks[task_id].response
