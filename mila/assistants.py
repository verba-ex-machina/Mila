"""Provide access to the OpenAI Assistants feature."""


import hashlib
import json

import openai

from mila import config
from mila.logging import logging
from mila.prompts import PROMPTS
from mila.tools import TOOLS


def assistant_hash() -> str:
    """Get the hash of the current assistant."""
    return hashlib.sha256(
        json.dumps(
            {
                "instructions": PROMPTS["system"],
                "tools": TOOLS.definitions,
                "model": config.MODEL,
                "version": config.VERSION,
            }
        ).encode("utf-8")
    ).hexdigest()


class Assistant:
    """Provide an abstraction for the OpenAI Assistants API."""

    def __init__(self, llm: openai.AsyncOpenAI, logger: logging.Logger):
        """Initialize the assistant."""
        self._llm = llm
        self._logger = logger
        self._assistant = None

    async def _spawn_assistant(self) -> None:
        """Link or spawn an assistant for the bot."""
        assistants = await self._llm.beta.assistants.list(limit=100)
        for assistant in assistants.data:
            if assistant.name == config.NAME:
                self._logger.info("Assistant found.")
                if (
                    "hash" not in assistant.metadata.keys()
                    or assistant.metadata["hash"] != assistant_hash()
                ):
                    await self._llm.beta.assistants.update(
                        assistant.id,
                        instructions=PROMPTS["system"],
                        tools=TOOLS.definitions,
                        model=config.MODEL,
                        metadata={
                            "hash": assistant_hash(),
                        },
                    )
                    self._logger.info("Assistant updated.")
                self._assistant = assistant
                return
        self._logger.info("No assistants found. New assistant spawned.")
        self._assistant = await self._llm.beta.assistants.create(
            instructions=PROMPTS["system"],
            name=config.NAME,
            model=config.MODEL,
            tools=TOOLS.definitions,
            metadata={
                "hash": assistant_hash(),
            },
        )

    async def _ready(self) -> None:
        """Get the assistant for the bot."""
        if not self._assistant:
            self._assistant = await self._spawn_assistant()

    async def id(self) -> str:
        """Get the ID of the assistant."""
        await self._ready()
        return self._assistant.id
