"""Provide the Mila library."""

import os

from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

from mila.prompts import PROMPTS


class Mila:
    """Represent Mila."""

    def __init__(self):
        """Initialize Mila."""
        self._llm = ChatOpenAI(
            model="gpt-3.5-turbo-16k",
            openai_api_key=os.getenv("OPENAI_API_KEY"),
        )

    def _craft_prompt(self) -> ChatPromptTemplate:
        """Craft a prompt for Mila."""
        return ChatPromptTemplate.from_messages(
            [
                ("system", PROMPTS["system"]),
                ("user", PROMPTS["user"]),
            ]
        )

    def _parse_context(self, context: list) -> tuple(tuple(str, str), str):
        """Parse the Discord chat context."""
        context = context[::-1]  # Discord provides LIFO.
        context.pop()  # Ignore Mila's *Thinking...* message.
        user = context[-1][0]
        message = context[-1][1]
        context = "\n".join([f"> {usr}: {msg}" for (usr, msg) in context[:-1]])
        return ((user, message), context)

    def prompt(self, context: list) -> str:
        """Prompt Mila with a message."""
        chain = self._craft_prompt() | self._llm
        ((user, message), context) = self._parse_context(context)
        print(f"{user}: {message}")
        response = chain.invoke(
            {
                "user": user,
                "message": message,
                "context": context,
            }
        )
        return response.content


MILA = Mila()
