"""Provide the Mila library."""

import logging

from mila.constants import DESCRIPTION
from mila.llm import LLM
from mila.prompts import PROMPTS


class Mila:
    """Represent Mila."""

    description = DESCRIPTION

    def __init__(self, logger: logging.Logger):
        """Initialize Mila."""
        self._logger = logger

    def prompt(self, query: str, context: str) -> str:
        """Prompt Mila with a message."""
        self._logger.info("Query: %s", query)
        chain = PROMPTS | LLM
        response = chain.invoke(
            {
                "query": query,
                "context": context,
            }
        )
        return response.content
