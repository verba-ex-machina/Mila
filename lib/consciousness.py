"""Provide Mila's AI functionality."""

import os

from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage

from lib.constants import SYSTEM_MESSAGE


class Consciousness:
    """Represent Mila's consciousness."""

    def __init__(self) -> None:
        """Initialize Mila's consciousness."""
        self._llm = ChatOpenAI(openai_api_key=os.getenv("OPENAI_API_KEY"))

    def prompt(self, message: str) -> str:
        """Prompt Mila with a message."""
        try:
            return self._llm.invoke(
                [
                    SystemMessage(
                        content=SYSTEM_MESSAGE,
                    ),
                    HumanMessage(content=message),
                ]
            ).content
        except Exception as err:
            return str(err)
