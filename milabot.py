#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""MilaBot: A Discord bot for Mila."""

import os

import discord
from discord.ext import tasks

TICK_TIME = 0.1  # How often to check for updates, in seconds.


class MilaBot(discord.Client):
    """Implement a Discord bot for interacting with Mila."""

    def __init__(self, *args, **kwargs):
        """Initialize MilaBot."""
        super().__init__(*args, **kwargs)

    @tasks.loop(seconds=TICK_TIME)
    async def tick(self) -> None:
        """Check for updates."""
        # Ask Mila for any completed tasks.
        # Collect the data from these tasks, including metadata.
        # From the metadata, determine where to send the response.
        # Send the response.

    async def on_message(self, message: discord.Message) -> None:
        """Handle a message seen by the bot."""
        # If the message is from MilaBot, ignore it.
        # Otherwise, gather the appropriate context,
        # append the metadata, and send it to Mila.

    async def on_ready(self) -> None:
        """Handle the bot being ready to use."""
        # Start the tick loop.
        # Print a message to the console.
        # Set the bot's status.
        # Set the bot's activity.
        # Print a message to the console.

    async def setup_hook(self) -> None:
        """Set up the bot."""
        self.tick.start()


def main():
    """Launch MilaBot."""
    intents = discord.Intents.default()
    intents.members = True
    intents.message_content = True
    bot = MilaBot(intents=intents)
    bot.run(os.getenv("DISCORD_TOKEN"))


if __name__ == "__main__":
    main()
