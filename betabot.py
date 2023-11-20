#!/usr/bin/env python3

"""Launch Mila as a Discord bot."""

import os

import discord
from discord.ext import tasks

from lib.logging import logging, LOGGER
from mila.constants import DESCRIPTION
from mila import Mila

CONTEXT_LIMIT = 20




class MilaBot(discord.Client):
    """Implement a Discord bot for interacting with Mila."""

    def __init__(self, mila: Mila, logger: logging.Logger, *args, **kwargs):
        """Initialize MilaBot."""
        super().__init__(*args, **kwargs)
        self._mila = mila
        self._logger = logger
        self._queries = {}

    @tasks.loop(seconds=1)
    async def tick(self) -> None:
        """Update all threads."""
        await self._check_queries()

    async def _check_queries(self) -> None:
        """Check for updates."""
        for task_id in list(self._queries.keys()):
            if await self._mila.check_completion(task_id):
                response = await self._mila.get_response(task_id)
                await self._queries[task_id].edit(content=response)
                self._queries.pop(task_id)

    async def _get_context(self, message: discord.Message):
        """Pull the message history and format it for Mila."""
        context = [
            f"{msg.author.name}: {msg.content}"
            async for msg in message.channel.history(limit=CONTEXT_LIMIT)
        ][::-1]
        return "> " + "\n> ".join(context)

    async def on_message(self, message: discord.Message):
        """Respond to incoming messages."""
        if message.author != self.user and (
            self.user.mentioned_in(message)
            or message.channel.type == discord.ChannelType.private
        ):
            task_id = await self._mila.handle_message(
                author=message.author.id,
                name=message.author.name,
                query=message.content,
                context=await self._get_context(message),
            )
            response = await message.reply("_Thinking..._")
            self._queries[task_id] = response

    async def on_ready(self) -> None:
        """Log a message when the bot is ready."""
        self._logger.info("Logged in as %s.", self.user)

    async def setup_hook(self) -> None:
        """Set up the bot's heartbeat."""
        self.tick.start()


def main():
    """Launch MilaBot."""
    intents = discord.Intents.default()
    intents.members = True
    intents.message_content = True
    bot = MilaBot(
        mila=Mila(logger=LOGGER),
        logger=LOGGER,
        description=DESCRIPTION,
        intents=intents,
    )
    bot.run(os.getenv("DISCORD_TOKEN"), log_handler=LOGGER.handlers[1])


if __name__ == "__main__":
    main()
