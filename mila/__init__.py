"""Provide the Mila library."""

import logging
import os

from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

from mila.prompts import PROMPTS


class Mila:
    """Represent Mila."""

    def __init__(self, logger: logging.Logger):
        """Initialize Mila."""
        self._logger = logger
        self._llm = ChatOpenAI(
            model="gpt-3.5-turbo-16k",
            openai_api_key=os.getenv("OPENAI_API_KEY"),
        )
        self._logger.info("Mila initialized.")

    def _craft_prompt(self) -> ChatPromptTemplate:
        """Craft a prompt for Mila."""
        return ChatPromptTemplate.from_messages(
            [
                ("system", PROMPTS["system"]),
                ("user", PROMPTS["user"]),
            ]
        )

    def prompt(self, query: str, context: str) -> str:
        """Prompt Mila with a message."""
        self._logger.info("Query: %s", query)
        chain = self._craft_prompt() | self._llm
        response = chain.invoke(
            {
                "query": query,
                "context": context,
            }
        )
        return response.content
