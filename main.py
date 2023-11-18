#!/usr/bin/env python3

"""Launch Mila as a service."""

import os

import discord

from lib.logging import LOGGER
from mila import Mila
from mila.constants import DESCRIPTION


class MilaBot(discord.Client):
    """Implement a Discord Bot for Mila."""

    def __init__(self, mila, logger, *args, **kwargs):
        """Initialize MilaBot."""
        super().__init__(*args, **kwargs)
        self._logger = logger
        self._mila = mila

    async def _parse_history(self, message: discord.Message) -> tuple:
        """Gather context for Mila."""
        context = [
            (msg.author.display_name, msg.content)
            async for msg in message.channel.history(limit=20)
        ][::-1]
        context.pop()  # Ignore Mila's *Thinking...* message.
        context_str = "\n".join(f"> {msg[0]}: {msg[1]}" for msg in context)
        query = f"{message.author.display_name}: {message.content}"
        return (query, context_str)

    async def on_ready(self):
        """Print a message when the bot is ready."""
        self._logger.info("Logged in as %s.", self.user)

    async def on_message(self, message):
        """Respond to messages."""
        if message.author == self.user:
            return
        # Respond to DMs and messages that mention the bot.
        if (
            self.user.mentioned_in(message)
            or message.channel.type == discord.ChannelType.private
        ):
            msg = await message.reply("_Thinking..._")
            (query, context) = await self._parse_history(message)
            # Prompt Mila with the message.
            response = self._mila.prompt(query, context)
            await msg.edit(content=response)


if __name__ == "__main__":
    mila = Mila(logger=LOGGER)
    intents = discord.Intents.default()
    intents.members = True
    intents.message_content = True
    bot = MilaBot(
        mila=mila, logger=LOGGER, description=mila.description, intents=intents
    )
    bot.run(os.getenv("DISCORD_TOKEN"), log_handler=LOGGER.handlers[1])
