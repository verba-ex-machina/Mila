#!/usr/bin/env python3

"""Launch Mila as a Discord bot."""

import os

import discord
from discord.ext import tasks

from mila import Mila, config
from mila.logging import LOGGER

CONTEXT_LIMIT = 5 # How many previous Discord messages to include in context.


class MilaBot(discord.Client):
    """Implement a Discord bot for interacting with Mila."""

    def __init__(self, mila: Mila, *args, **kwargs):
        """Initialize MilaBot."""
        super().__init__(*args, **kwargs)
        self._mila = mila
        self._threads = {}

    @tasks.loop(seconds=1)
    async def tick(self) -> None:
        """Check for updates."""
        for thread_id in list(self._threads.keys()):
            if await self._mila.check_completion(thread_id):
                response = await self._mila.get_response(thread_id)
                if len(response) > 2000:
                    # Response is too long for Discord. Split it into chunks,
                    # but avoid splitting in the middle of a line.
                    message = self._threads[thread_id]
                    chunks = response.split("\n")
                    response = ""
                    for chunk in chunks:
                        if len(response) + len(chunk) > 2000:
                            await message.edit(content=response)
                            message = await message.reply("_Responding..._")
                            response = "(continued)\n"
                        response += chunk + "\n"
                    await message.edit(content=response)
                else:
                    await self._threads[thread_id].edit(content=response)
                self._threads.pop(thread_id)

    async def _get_context(self, message: discord.Message):
        """Pull the message history and format it for Mila."""
        chat_context = "\n".join(
            [
                f"> {msg.author.name}: {msg.content}"
                async for msg in message.channel.history(limit=CONTEXT_LIMIT)
            ][::-1]
        )
        if message.guild:
            context = f"You in the {message.guild.name} Discord server. "
        else:
            context = "You are in a private Discord direct-message chat. "
        context += (
            f"Here are the last {CONTEXT_LIMIT} messages in the chat:\n\n"
            + chat_context
        )
        return await self._sub_usernames(context)

    async def _sub_usernames(self, message: str) -> str:
        """Substitute Discord usernames for user IDs."""
        for user in self.users:
            message = message.replace(f"<@{user.id}>", user.name)
        return message

    async def on_message(self, message: discord.Message):
        """Respond to incoming messages."""
        if message.author != self.user and (
            self.user.mentioned_in(message)
            or message.channel.type == discord.ChannelType.private
        ):
            thread_id = await self._mila.handle_message(
                author=message.author.id,
                name=message.author.name,
                query=await self._sub_usernames(message.content),
                context=await self._get_context(message),
            )
            response = await message.reply("_Thinking..._")
            self._threads[thread_id] = response

    async def on_ready(self) -> None:
        """Log a message when the bot is ready."""
        LOGGER.info("Logged in as %s.", self.user)

    async def setup_hook(self) -> None:
        """Set up the bot's heartbeat."""
        self.tick.start()


def main():
    """Launch MilaBot."""
    intents = discord.Intents.default()
    intents.members = True
    intents.message_content = True
    mila = Mila()
    bot = MilaBot(
        mila=mila,
        description=config.DESCRIPTION,
        intents=intents,
    )
    bot.run(
        os.getenv("DISCORD_TOKEN"),
        log_handler=LOGGER.handlers[1],
        log_formatter=LOGGER.handlers[1].formatter,
    )


if __name__ == "__main__":
    main()
