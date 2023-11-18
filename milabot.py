#!/usr/bin/env python3

"""Launch Mila as a Discord bot."""

import os
from logging import Logger

import discord

from lib.logging import LOGGER
from mila import Mila, MilaRequest

CHAT_CONTEXT_LENGTH = 20


class MilaBot(discord.Client):
    """Implement a Discord bot for interacting with Mila."""

    def __init__(self, mila: Mila, logger: Logger, *args, **kwargs):
        """Initialize MilaBot."""
        super().__init__(*args, **kwargs)
        self._logger = logger
        self._mila = mila

    async def _format_request(self, history: list) -> MilaRequest:
        """Gather the query and related context for Mila."""
        query = history.pop()  # Get the user's query.
        history = "> " + "\n> ".join(history)
        return MilaRequest(query=query, context=history)

    async def _get_chat_history(self, message: discord.Message) -> list:
        """Gather chat history from the given message."""
        context = [
            f"{msg.author.display_name}: {msg.content}"
            async for msg in message.channel.history(limit=CHAT_CONTEXT_LENGTH)
        ][
            ::-1
        ]  # Discord returns messages LIFO.
        return context

    async def on_message(self, message):
        """Respond to messages."""
        if (
            self.user.mentioned_in(message)
            or message.channel.type == discord.ChannelType.private
        ) and message.author != self.user:
            history = await self._get_chat_history(message)
            request = await self._format_request(history)
            reply = await message.reply("_Thinking..._")
            response = await self._mila.prompt(request)
            await reply.edit(content=response)

    async def on_ready(self):
        """Print a message when the bot is ready."""
        self._logger.info("Logged in as %s.", self.user)


def launch_milabot():
    """Launch MilaBot."""
    mila = Mila(logger=LOGGER)
    intents = discord.Intents.default()
    intents.members = True
    intents.message_content = True
    bot = MilaBot(
        mila=mila,
        logger=LOGGER,
        description=mila.description,
        intents=intents,
    )
    bot.run(os.getenv("DISCORD_TOKEN"), log_handler=LOGGER.handlers[1])


if __name__ == "__main__":
    launch_milabot()
