#!/usr/bin/env python3

"""Launch Mila as a Discord bot."""

# import asyncio
# import json
# import time
import os
from logging import Logger

import discord
from discord.ext import tasks
from openai import AsyncOpenAI

from lib.logging import LOGGER
from mila.constants import DESCRIPTION, MODEL, NAME
from mila.prompts import PROMPTS

CONTEXT_LIMIT = 20

async def get_horoscope(star_sign: str) -> str:
    """Get the horoscope for a given star sign."""
    print("Function called: get_horoscope")
    return f"Your horoscope for {star_sign} is: Memento mori."

def make_subs(prompt: str, query: str, context: str):
    """Make substitutions for the query and context."""
    sub_dict = {
        "query": query,
        "context": context,
    }
    return prompt.format(**sub_dict)


"""
make_subs(
                [
                    {
                        "role": "user",
                        "content": PROMPTS["user"],
                    }
                ],
                query,
                context,
            )
    run = await llm.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id,
    )
    tool_outputs = []
    while True:
        run = await llm.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id,
        )
        if run.status == "completed":
            break
        elif run.status in [
            "cancelled",
            "expired",
            "failed",
        ]:
            raise RuntimeError(f"Run failed: {run.status}")
        elif run.status == "requires_action":
            for (
                tool_call
            ) in run.required_action.submit_tool_outputs.tool_calls:
                arguments = json.loads(tool_call.function.arguments)
                name = tool_call.function.name
                if name == "get_horoscope":
                    response = await get_horoscope(**arguments)
                    id = tool_call.id
                    tool_outputs.append(
                        {
                            "tool_call_id": id,
                            "output": response,
                        }
                    )
                else:
                    raise RuntimeError(f"Unknown tool call: {name}")
            run = await llm.beta.threads.runs.submit_tool_outputs(
                thread_id=thread.id,
                run_id=run.id,
                tool_outputs=tool_outputs,
            )
        else:
            time.sleep(1)
    MESSAGES = await llm.beta.threads.messages.list(
        thread_id=thread.id,
    )
    for message in MESSAGES.data:
        for content in message.content:
            print(content.text.value)
    await llm.beta.assistants.delete(
        assistant_id=assistant.id,
    )
    await llm.beta.threads.delete(
        thread_id=thread.id,
    )


if __name__ == "__main__":
    asyncio.run(main())
"""


class Mila:
    """Represent the Mila assistant."""

    _tool_definitions = [
        {
            "name": "get_horoscope",
            "function": get_horoscope,
            "description": "Get the horoscope for a given star sign.",
            "properties": {
                "star_sign": {
                    "type": "string",
                    "description": "The star sign for which the horoscope is intended.",
                }
            },
            "required": ["star_sign"],
        }
    ]

    def __init__(self, logger: Logger):
        """Initialize Mila."""
        self._llm = AsyncOpenAI()
        self._logger = logger
        self._assistant_id = None
        self._logger.info("Mila class initialized.")
        self._threads = {}
        self._runs = {}
    
    async def _spawn_assistant(self) -> None:
        """Spawn a new assistant for the bot."""
        assistant = await self._llm.beta.assistants.create(
            instructions=PROMPTS["system"],
            name=NAME,
            model=MODEL,
            tools=self._tools,
            metadata={},
        )
        self._assistant_id = assistant.id
    
    async def _spawn_thread(self, author: str, name: str):
        """Spawn a new thread for the bot."""
        thread = await self._llm.beta.threads.create(
            messages=[],
            metadata={
                "author": author,
                "name": name,
            },
        )
        self._threads[author] = thread.id

    @property
    def _tools(self) -> list:
        """Return an OpenAI-formatted list of tool definitions."""
        return [
            {
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool["description"],
                    "parameters": {
                        "type": "object",
                        "properties": tool["properties"],
                        "required": tool["required"],
                    },
                },
            }
            for tool in self._tool_definitions
        ]

    async def handle_message(
            self,
            author: str,
            name: str,
            query: str,
            context: str,
    ) -> str:
        """Handle an incoming message."""
        self._logger.info(
            "Message received from %s (%s): %s",
            author,
            name,
            query,
        )
        if not self._assistant_id:
            await self._spawn_assistant()
        if author not in self._threads:
            await self._spawn_thread(author, name)
        thread = self._threads[author]
        await self._llm.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=make_subs(PROMPTS["user"], query, context)
        )
        run = self._llm.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=self._assistant_id,
        )
        self._runs[run.id] = thread.id
        return run.id


class MilaBot(discord.Client):
    """Implement a Discord bot for interacting with Mila."""

    def __init__(self, mila: Mila, logger: Logger, *args, **kwargs):
        """Initialize MilaBot."""
        super().__init__(*args, **kwargs)
        self._mila = mila
        self._logger = logger
        self._logger.info("MilaBot class initialized.")
        self._queries = {}

    @tasks.loop(seconds=1)
    async def tick(self) -> None:
        """Update all threads."""
        await self._check_queries()

    async def _check_queries(self) -> None:
        """Check for updates."""
    
    async def _get_context(self, message: discord.Message):
        """Pull the message history and format it for Mila."""
        history = message.channel.history(limit=CONTEXT_LIMIT)
        context = [
            f"{message.author.name}: {message.content}"
            for message in history[::-1]
        ]
        return "> " + "\n> ".join(context)

    async def on_message(self, message: discord.Message):
        """Respond to incoming messages."""
        if message.author != self.user and (
            self.user.mentioned_in(message)
            or message.channel.type == discord.ChannelType.private
        ):
            task_id = await self._mila.handle_message(
                author=message.author.id,
                name=message.author.name,
                query=message.content,
                context=await self._get_context(message),
            )
            response = await message.reply("_Thinking..._")
            self._queries[task_id] = response

    async def on_ready(self) -> None:
        """Log a message when the bot is ready."""
        self._logger.info("Logged in as %s.", self.user)

    async def setup_hook(self) -> None:
        """Set up the bot's heartbeat."""
        self.tick.start()


def main():
    """Launch the Tiny Assistant demo."""
    intents = discord.Intents.default()
    intents.members = True
    intents.message_content = True
    bot = MilaBot(
        mila=Mila(logger=LOGGER),
        logger=LOGGER,
        description=DESCRIPTION,
        intents=intents,
    )
    bot.run(os.getenv("DISCORD_TOKEN"), log_handler=LOGGER.handlers[1])


if __name__ == "__main__":
    main()
