"""Provide the Mila library."""

import os

from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage

DESCRIPTION = "Mila: The Mindful, Interactive Lifestyle Assistant"
SYSTEM_MESSAGE = f"You are {DESCRIPTION}. You are an ethical AI."


class Mila:
    """Represent Mila."""

    description = DESCRIPTION

    def __init__(self):
        """Initialize Mila."""
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


MILA = Mila()
