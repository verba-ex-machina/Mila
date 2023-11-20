"""Provide the Mila library."""

import logging
from hashlib import sha256

from openai import AsyncOpenAI

from mila.constants import DESCRIPTION, MODEL
from mila.prompts import PROMPTS

LLM = AsyncOpenAI()


def make_subs(prompt_list: list, query: str, context: str) -> str:
    """Make substitutions to the query and context."""
    sub_dict = {
        "query": query,
        "context": context,
    }
    for prompt in prompt_list:
        prompt["content"] = prompt["content"].format(**sub_dict)
    return prompt_list


class Mila:
    """Represent Mila."""

    def __init__(self, logger: logging.Logger):
        """Initialize Mila."""
        self.description = DESCRIPTION
        self._assistant = None
        self._logger = logger
        self._threads = {}
