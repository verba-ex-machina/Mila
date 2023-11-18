"""Provide prompts for Mila."""

from langchain.chat_models.base import BaseChatModel
from langchain.prompts import ChatPromptTemplate

from mila.constants import DESCRIPTION, PROMPT_PATH


class Prompts:
    """Represent the library of Mila's prompts."""

    _subs = {
        # Replace values in prompt files on-the-fly.
        "DESCRIPTION": DESCRIPTION,
    }

    def _make_subs(self, content: str) -> str:
        """Make substitutions in a string."""
        for key, value in self._subs.items():
            content = content.replace(f"{{{key}}}", value)
        return content

    def __getitem__(self, name: str) -> str:
        """Get a prompt by name."""
        with open(f"{PROMPT_PATH}{name}.txt", "r", encoding="utf-8") as file:
            return self._make_subs(file.read().strip())

    def __or__(self, other: BaseChatModel):
        """Implement the OR operator."""
        return (
            ChatPromptTemplate.from_messages(
                [
                    ("system", self["system"]),
                    ("user", self["user"]),
                ]
            )
            | other
        )


PROMPTS = Prompts()
