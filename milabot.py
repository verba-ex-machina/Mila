#!/usr/bin/env python3

"""Launch Mila as a Discord bot."""

import os
from logging import Logger

import discord
from discord.ext import tasks

from lib.logging import LOGGER
from mila import Mila

CHAT_CONTEXT_LENGTH = 20


class MilaBot(discord.Client):
    """Implement a Discord bot for interacting with Mila."""

    class BotTask:
        """Represent a task to be executed by Mila."""

        def __init__(self, query: str, context: str, reply: discord.Message):
            """Initialize the task."""
            self.query = query
            self.context = context
            self.reply = reply
            self.attempts = 0
            self.status = "pending"

        async def update(self, message: str):
            """Update the task's reply message."""
            await self.reply.edit(content=message)

    def __init__(self, mila: Mila, logger: Logger, *args, **kwargs):
        """Initialize MilaBot."""
        super().__init__(*args, **kwargs)
        self._logger = logger
        self._mila = mila
        self._tasks = {}

    async def _new_task(self, message: discord.Message) -> BotTask:
        """Gather the query and related context for Mila."""
        history = await self._get_chat_history(message)
        query = history.pop()  # Get the user's query.
        context = "> " + "\n> ".join(history)
        reply = await message.reply("_Thinking..._")
        return self.BotTask(query=query, context=context, reply=reply)

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
            task = await self._new_task(message)
            task_id = await self._mila.add_task(task.query, task.context)
            self._tasks[task_id] = task

    async def on_ready(self):
        """Print a message when the bot is ready."""
        self._logger.info("Logged in as %s.", self.user)

    async def setup_hook(self) -> None:
        """Set up the bot."""
        self.tick.start()

    @tasks.loop(seconds=1)
    async def tick(self):
        """Update all tasks."""
        for task_id in list(self._tasks.keys()):
            task = self._tasks[task_id]
            if task.status == "pending":
                # Check to see if the task is complete.
                try:
                    if await self._mila.check(task_id):
                        task.status = "complete"
                    task.attempts = 0
                except KeyError:
                    if task.attempts > 3:
                        self._logger.warning("Task %s not found.", task_id)
                        task.status = "drop"
                    task.attempts += 1
            if task.status == "complete":
                # Send the response.
                response = self._mila.get_response(task_id)
                await task.update(response)
                self._logger.info("Task %s response sent!", task_id)
                task.status = "drop"
            if task.status == "drop":
                self._mila.drop_task(task_id)
                del self._tasks[task_id]


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
