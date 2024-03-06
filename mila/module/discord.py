"""Provide Discord connectivity for Mila."""

import asyncio
import os
import queue
from multiprocessing import Process, Queue
from typing import List

import discord
from discord.ext import tasks

from mila.base.constants import TICK
from mila.base.interfaces import TaskIO
from mila.base.types import MilaTask
from mila.module.fake import FakeIO


class DiscordClient(discord.Client):
    """Implement a minimalist Discord client process."""

    def __init__(
        self, recv_queue: Queue, send_queue: Queue, *args, **kwargs
    ) -> None:
        """Initialize the DiscordClient."""
        super().__init__(*args, **kwargs)
        self._ctx_limit = 5
        self.status = discord.Status.offline
        self.activity = discord.Game(name="Electric Sheep")
        self._queue = {
            "recv": recv_queue,
            "send": send_queue,
        }

    async def _get_context(self, message: discord.Message) -> str:
        """Pull the message history and format it for Mila."""
        chat_context = "\n".join(
            [
                f"> {msg.author.name}: {msg.content}"
                async for msg in message.channel.history(limit=self._ctx_limit)
            ][::-1]
        )
        if message.guild:
            context = f"You in the {message.guild.name} Discord server. "
        else:
            context = "You are in a private Discord direct-message chat. "
        context += (
            f"Here are the last {self._ctx_limit} messages in the chat:\n\n"
            + chat_context
        )
        return await self._sub_usernames(context)

    @tasks.loop(seconds=TICK)
    async def _handle_received_tasks(self) -> None:
        """Handle tasks received from Mila."""
        try:
            task: MilaTask = self._queue["send"].get_nowait()
        except queue.Empty:
            pass
        else:
            if task.context == "COMMAND":
                if task.content == "EXIT":
                    await self.teardown_hook()
            else:
                await self._send_message(task)

    async def _send_message(self, task: MilaTask) -> None:
        """Send a message."""
        # This currently assumes every message is a reply to another message.
        channel = await self.fetch_channel(task.destination["channel_id"])
        message = await channel.fetch_message(task.destination["message_id"])
        reply = await message.reply("_Responding..._")
        if len(task.content) > 2000:
            chunks = task.content.split("\n")
            response = ""
            for chunk in chunks:
                if len(response) + len(chunk) > 2000:
                    await reply.edit(content=response)
                    reply = await reply.reply("_Responding..._")
                    response = "(continued)\n"
                response += chunk + "\n"
            if response.strip():
                await reply.edit(content=response.strip())
        else:
            await reply.edit(content=task.content)

    async def _make_task(self, message: discord.Message) -> MilaTask:
        """Create a MilaTask from a Discord message."""
        task = MilaTask(
            context=await self._get_context(message),
            content=message.content,
            source={
                "author": {
                    "id": message.author.id,
                    "name": message.author.name,
                    "nick": message.author.display_name,
                },
                "channel_id": message.channel.id,
                "message_id": message.id,
                "guild": (
                    {}
                    if not message.guild
                    else {
                        "id": message.guild.id,
                        "name": message.guild.name,
                    }
                ),
            },
        )
        return task

    async def _sub_usernames(self, text: str) -> str:
        """Substitute user mentions with usernames in the text."""
        for user in self.users:
            text = text.replace(f"<@{user.id}>", user.name)
        return text

    async def on_message(self, message: discord.Message) -> None:
        """Handle incoming messages."""
        if message.author != self.user and (
            self.user.mentioned_in(message)
            or message.channel.type == discord.ChannelType.private
        ):
            task = await self._make_task(message)
            self._queue["recv"].put(task)

    async def on_ready(self) -> None:
        """Log in to Discord."""
        self.status = discord.Status.online
        self.activity = discord.Game(name="The Sims IRL")
        await self.change_presence(status=self.status, activity=self.activity)

    async def setup_hook(self) -> None:
        """Set up the Discord client."""
        # pylint: disable=E1101
        self._handle_received_tasks.start()

    async def teardown_hook(self) -> None:
        """Tear down the Discord client."""
        # pylint: disable=E1101
        self._handle_received_tasks.stop()
        self.status = discord.Status.offline
        self.activity = discord.Game(name="Electric Sheep")
        await self.change_presence(status=self.status, activity=self.activity)
        await self.http.close()
        await self.close()


class DiscordIO(TaskIO):
    """Implement a Discord TaskIO adapter."""

    def __init__(self) -> None:
        """Initialize the DiscordIO."""
        super().__init__()
        self._client = None
        self._process = None
        self._recv_queue = Queue()
        self._send_queue = Queue()

    def _launch(self) -> None:
        """Launch the Discord Client."""
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True
        self._client = DiscordClient(
            recv_queue=self._recv_queue,
            send_queue=self._send_queue,
            intents=intents,
        )
        self._client.run(os.getenv("DISCORD_TOKEN"))

    async def recv(self) -> List[MilaTask]:
        """Receive all queued tasks from Discord."""
        task_list = []
        while True:
            try:
                task: MilaTask = self._recv_queue.get_nowait()
            except queue.Empty:
                break
            task.source["handler"] = self.__class__.__name__
            task_list.append(task)
        return task_list

    async def send(self, task_list: List[MilaTask]) -> None:
        """Send a list of tasks to Discord."""
        for task in task_list:
            self._send_queue.put(task)

    async def setup(self) -> None:
        """Start the Discord Client."""
        self._process = Process(target=self._launch)
        self._process.start()

    async def teardown(self) -> None:
        """Stop the Discord Client."""
        kill_msg = MilaTask(content="EXIT", context="COMMAND")
        self._send_queue.put(kill_msg)
        self._process.join()


async def demo():
    """Run an echo-server demo of the Discord module."""
    running = True
    async with DiscordIO() as discord_io:
        async with FakeIO() as fakeio:
            while running:
                task_list = await discord_io.recv()
                if any(task.content == "exit" for task in task_list):
                    running = False
                    break
                await fakeio.send(task_list)
                await discord_io.send(await fakeio.recv())
                await asyncio.sleep(TICK)


if __name__ == "__main__":
    asyncio.run(demo())
