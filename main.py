#!/usr/bin/env python3

"""Launch Mila as a service."""

import os

import discord

from mila import MILA

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
            msg = await message.reply("_Thinking..._")
            response = MILA.prompt(message.content)
            await msg.delete()
            await message.reply(content=response)


BOT = MilaBot(description=MILA.description, intents=INTENTS)


def main():
    """Launch Mila as a service."""
    BOT.run(os.getenv("DISCORD_TOKEN"))


if __name__ == "__main__":
    main()
