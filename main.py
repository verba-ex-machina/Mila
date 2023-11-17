#!/usr/bin/env python3

"""Launch Mila as a service."""

import os

import discord

from lib.logging import logger
from mila import Mila
from mila.constants import DESCRIPTION

INTENTS = discord.Intents.default()
INTENTS.members = True
INTENTS.message_content = True


class MilaBot(discord.Client):
    """Implement a Discord Bot for Mila."""

    def __init__(self, _logger, *args, **kwargs):
        """Initialize MilaBot."""
        super().__init__(*args, **kwargs)
        self._logger = _logger
        self._mila = Mila(logger=self._logger)

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
            await msg.delete()
            await message.reply(content=response)


if __name__ == "__main__":
    bot = MilaBot(_logger=logger, description=DESCRIPTION, intents=INTENTS)
    bot.run(os.getenv("DISCORD_TOKEN"), log_handler=logger.handlers[1])
