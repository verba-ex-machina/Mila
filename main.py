#!/usr/bin/env python3

"""Launch Mila as a service."""

import os

import discord

from lib import Mila
from lib.constants import DESCRIPTION

MILA = Mila()

INTENTS = discord.Intents.default()
INTENTS.members = True
INTENTS.message_content = True


class MilaBot(discord.Client):
    """Implement a Discord Bot for Mila."""

    async def on_ready(self):
        """Print a message when the bot is ready."""
        print(f"Logged in as {self.user}.")

    async def on_message(self, message):
        """Respond to messages."""
        if message.author == self.user:
            return
        # Respond to messages that mention the bot.
        if self.user.mentioned_in(message):
            await message.channel.send(MILA.prompt(message.content))


BOT = MilaBot(description=DESCRIPTION, intents=INTENTS)


def main():
    """Launch Mila as a service."""
    BOT.run(os.getenv("DISCORD_TOKEN"))


if __name__ == "__main__":
    main()
