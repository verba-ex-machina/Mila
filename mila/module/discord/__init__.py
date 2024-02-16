"""Provide Discord modules for Mila."""

import os
import queue
from multiprocessing import Process, Queue
from typing import Union

import discord
from discord.ext import tasks

from mila.base.interfaces import TaskIO
from mila.base.types import MilaTask


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

    @tasks.loop(seconds=0.1)
    async def _handle_received_tasks(self) -> None:
        """Handle tasks received from Mila."""
        try:
            task = self._queue["send"].get_nowait()
        except queue.Empty:
            pass
        else:
            channel = await self.fetch_channel(task.meta["channel_id"])
            message = await channel.fetch_message(task.meta["message_id"])
            reply = await message.reply("_Responding..._")
            if len(task.response) > 2000:
                # Response is too long for Discord. Split it into chunks,
                # but avoid splitting in the middle of a line.
                chunks = task.response.split("\n")
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
                await reply.edit(content=task.response)

    async def _make_task(self, message: discord.Message) -> MilaTask:
        """Create a MilaTask from a Discord message."""
        msg_data = {
            "author": message.author.name,
            "author_id": message.author.id,
            "author_nick": message.author.display_name,
            "message_id": message.id,
            "channel_id": message.channel.id,
            "guild": message.guild.name if message.guild else None,
            "guild_id": message.guild.id if message.guild else None,
        }
        task = MilaTask(
            context=await self._get_context(message),
            prompt=message.content,
            meta=msg_data,
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
        print(f"Logged in as {self.user}")

    async def setup_hook(self) -> None:
        """Set up the Discord client."""
        # pylint: disable=E1101
        self._handle_received_tasks.start()


class DiscordIO(TaskIO):
    """Implement a Discord TaskIO adapter."""

    def __init__(self) -> None:
        """Initialize the DiscordIO."""
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

    async def recv(self) -> Union[MilaTask, None]:
        """Receive a task from Discord."""
        try:
            task = self._recv_queue.get_nowait()
        except queue.Empty:
            return None
        return task

    async def send(self, task: MilaTask) -> None:
        """Send a task to Discord."""
        self._send_queue.put(task)

    def start(self) -> None:
        """Start the Discord Client."""
        self._process = Process(target=self._launch)
        self._process.start()
