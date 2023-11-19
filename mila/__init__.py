"""Provide the Mila library."""

import logging
from hashlib import sha256

from mila.constants import DESCRIPTION
from mila.llm import LLM
from mila.prompts import PROMPTS




class Mila:
    """Represent Mila."""
    
    class MilaTask:
        """Represent a single request to the Mila AI."""

        def __init__(self, query: str, context: str):
            """Initialize the task."""
            self.query = query
            self.context = context

    def __init__(self, logger: logging.Logger):
        """Initialize Mila."""
        self.description = DESCRIPTION
        self._logger = logger
        self._tasks = {}

    def add_task(self, query: str, context: str) -> str:
        """Add a task to Mila."""
        task_id = sha256((query + context).encode("utf-8")).hexdigest()
        self._tasks[task_id] = self.MilaTask(query, context)
        return task_id

    async def prompt(self, request: MilaTask) -> str:
        """Prompt Mila with a message."""
        self._logger.info("Query: %s", request.query)
        chain = PROMPTS | LLM
        response = await chain.ainvoke(
            {
                "query": request.query,
                "context": request.context,
            }
        )
        return response.content
