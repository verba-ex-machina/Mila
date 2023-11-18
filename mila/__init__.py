"""Provide the Mila library."""

import logging
from hashlib import sha256


from mila.constants import DESCRIPTION
from mila.llm import LLM
from mila.prompts import PROMPTS


class MilaRequest:
    """Represent a single request to the Mila AI."""
    
    def __init__(self, query: str, context: str):
        """Initialize a MilaRequest."""
        self.id = sha256((query + context).encode("utf-8")).hexdigest()
        self.query = query
        self.context = context


class Mila:
    """Represent Mila."""

    description = DESCRIPTION

    def __init__(self, logger: logging.Logger):
        """Initialize Mila."""
        self._logger = logger

    async def prompt(self, request: MilaRequest) -> str:
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
