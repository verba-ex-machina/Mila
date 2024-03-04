"""Provide access to the OpenAI Assistants feature."""


import hashlib
import json

from . import config
from .llm import LLM
from .logging import LOGGER
from .prompts import PROMPTS
from .tools import TOOLS


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

    def __init__(self):
        """Initialize the assistant."""
        self._assistant = None

    async def _spawn_assistant(self) -> None:
        """Link or spawn an assistant for the bot."""
        assistants = await LLM.beta.assistants.list(limit=100)
        for assistant in assistants.data:
            if assistant.name == config.NAME:
                LOGGER.info("Assistant found.")
                if (
                    "hash" not in assistant.metadata.keys()
                    or assistant.metadata["hash"] != assistant_hash()
                ):
                    await LLM.beta.assistants.update(
                        assistant.id,
                        instructions=PROMPTS["system"],
                        tools=TOOLS.definitions,
                        model=config.MODEL,
                        metadata={
                            "hash": assistant_hash(),
                        },
                    )
                    LOGGER.info("Assistant updated.")
                self._assistant = assistant
                return
        LOGGER.info("No assistants found. New assistant spawned.")
        self._assistant = await LLM.beta.assistants.create(
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
            await self._spawn_assistant()

    async def id(self) -> str:
        """Get the ID of the assistant."""
        await self._ready()
        return self._assistant.id
