#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""MilaBot: A Discord bot for Mila."""

import os

import discord
import datetime
from discord.ext import tasks
import queue
from mila import Mila

TICK_TIME = 0.1  # How often to check for updates, in seconds.


class MilaBot(discord.Client):
    """Implement a Discord bot for interacting with Mila."""

    def __init__(self, *args, **kwargs):
        """Initialize MilaBot."""
        super().__init__(*args, **kwargs)
        self._input_queue = queue.SimpleQueue()
        self._tasks = {}

    @tasks.loop(seconds=TICK_TIME)
    async def tick(self) -> None:
        """Check for updates."""
        new_message = None
        try:
            new_message = self._input_queue.get_nowait()
        except queue.Empty:
            pass
        if new_message:
            response = await new_message.reply("_Thinking..._")
            task_id = "abc123" # TODO: Get the task ID from Mila.
            self._tasks[task_id] = response
        for id, response in self._tasks.items():
            pass
        # If there are completed tasks:
        #     For each completed task:
        #         Get the response from Mila.
        #         If the response is too long for Discord:
        #             Split the response into chunks.
        #             For each chunk:
        #                 If the chunk is the first:
        #                     Edit the placeholder message.
        #                 Else:
        #                     Send a new message in response to the previous chunk.
        #         Else:
        #             Edit the placeholder message.
        #         Remove the task ID from the list.

    async def on_message(self, message: discord.Message) -> None:
        """Handle a message seen by the bot."""
        if message.author != self.user and (
            self.user.mentioned_in(message)
            or message.channel.type == discord.ChannelType.private
        ):
            self._input_queue.put(message)

    async def on_ready(self) -> None:
        """Handle the bot being ready to use."""
        self.status = discord.Status.online
        year = datetime.datetime.now().year
        activity = discord.Game(name=f"Personal Assistant Simulator {year}")
        await self.change_presence(activity=activity)
        print(f"Logged in as {self.user.name} (ID: {self.user.id})")

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
