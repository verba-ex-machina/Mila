#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""MilaBot: A Discord bot for Mila."""

import os

import discord
import datetime
from discord.ext import tasks
import queue
from mila import Mila

CONTEXT_LIMIT = 5  # How many previous Discord messages to include in context.
TICK_TIME = 0.1  # How often to check for updates, in seconds.


class MilaBot(discord.Client):
    """Implement a Discord bot for interacting with Mila."""

    def __init__(self, mila: Mila, *args, **kwargs):
        """Initialize MilaBot."""
        super().__init__(*args, **kwargs)
        self._input_queue = queue.SimpleQueue()
        self._mila = mila
        self._tasks = {}
    
    async def __get_context(self, message: discord.Message):
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
        context += f"Here are the last {CONTEXT_LIMIT} messages:\n\n"
        return self._sub_usernames(context + chat_context)
    
    def _log(self, message: str) -> None:
        """Log a message."""
        self._mila.get_logger().info(message)

    async def _sub_usernames(self, message: str) -> str:
        """Substitute Discord usernames for user IDs."""
        for user in self.users:
            message = message.replace(f"<@{user.id}>", user.name)
        return message

    @tasks.loop(seconds=TICK_TIME)
    async def _tick(self) -> None:
        """Check for updates."""
        new_message = None
        try:
            new_message = self._input_queue.get_nowait()
        except queue.Empty:
            pass
        if new_message:
            response = await new_message.reply("_Thinking..._")
            context = await self.__get_context(new_message)
            query = (
                f"There's a new query from {new_message.author.name}. "
                + f"Here's the context: {context}\n\n"
                + f"The query from {new_message.author.name} is as follows:\n"
                + f"{await self._sub_usernames(new_message.content)}"
            )
            task_id = await self._mila.new_task(query)
            self._tasks[task_id] = response
        completed_tasks = []
        for id, response in self._tasks.items():
            if await self._mila.task_complete(id):
                response = await self._mila.get_response(id)
                if len(response) > 2000:
                    # Response is too long for Discord. Split it into chunks,
                    # but avoid splitting in the middle of a line.
                    message = self._tasks[id]
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
                    await self._tasks[id].edit(content=response)
                completed_tasks.append(id)
        for id in completed_tasks:
            self._tasks.pop(id)

    async def on_message(self, message: discord.Message) -> None:
        """Handle a message seen by the bot."""
        if message.author != self.user and (
            self.user.mentioned_in(message)
            or message.channel.type == discord.ChannelType.private
        ):
            self._input_queue.put(message)
            self._log(
                f"Received message from {message.author.name}: "
                + f"{await self._sub_usernames(message.content)}"
            )

    async def on_ready(self) -> None:
        """Handle the bot being ready to use."""
        self.status = discord.Status.online
        year = datetime.datetime.now().year
        activity = discord.Game(name=f"Personal Assistant Simulator {year}")
        await self.change_presence(activity=activity)
        self._log(f"Logged in as {self.user.name}. (ID: {self.user.id})")

    async def setup_hook(self) -> None:
        """Set up the bot."""
        self._log("Starting MilaBot.")
        self._tick.start()


def main():
    """Launch MilaBot."""
    intents = discord.Intents.default()
    intents.members = True
    intents.message_content = True
    mila = Mila()
    logger = mila.get_logger()
    bot = MilaBot(intents=intents, mila=mila)
    bot.run(
        os.getenv("DISCORD_TOKEN"),
        log_handler=logger.handlers[1],
        log_formatter=logger.handlers[1].formatter,
    )


if __name__ == "__main__":
    main()
