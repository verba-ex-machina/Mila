#!/usr/bin/env python3

"""Launch Mila as a Discord bot."""

import json
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
    LOGGER.info("Function called: get_horoscope")
    return f"Your horoscope for {star_sign} is: Memento mori."


def make_subs(prompt: str, query: str, context: str):
    """Make substitutions for the query and context."""
    sub_dict = {
        "query": query,
        "context": context,
    }
    return prompt.format(**sub_dict)


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
                    "description": "The user's star sign.",
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
        self._thread_ids = {}
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
        self._thread_ids[author] = thread.id

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

    async def check_completion(self, run_id: str) -> bool:
        """Check whether a query run is complete."""
        tool_outputs = []
        complete = False
        run = await self._llm.beta.threads.runs.retrieve(
            thread_id=self._runs[run_id],
            run_id=run_id,
        )
        if run.status == "completed":
            self._logger.info("Run completed.")
            complete = True
        elif run.status in [
            "cancelled",
            "expired",
            "failed",
        ]:
            self._logger.warn("Run failed: %s", run.status)
            await self._llm.beta.threads.runs.cancel(
                thread_id=self._runs[run_id],
                run_id=run_id,
            )
            complete = True
        elif run.status == "requires_action":
            self._logger.info("Run requires action.")
            for (
                tool_call
            ) in run.required_action.submit_tool_outputs.tool_calls:
                arguments = json.loads(tool_call.function.arguments)
                name = tool_call.function.name
                if name == "get_horoscope":
                    response = await get_horoscope(**arguments)
                    tool_call_id = tool_call.id
                    tool_outputs.append(
                        {
                            "tool_call_id": tool_call_id,
                            "output": response,
                        }
                    )
                else:
                    self._logger.warn("Unknown tool call: %s", name)
                    complete = True
            run = await self._llm.beta.threads.runs.submit_tool_outputs(
                thread_id=self._runs[run_id],
                run_id=run_id,
                tool_outputs=tool_outputs,
            )
        return complete

    async def get_response(self, run_id: str) -> str:
        """Retrieve the final response from a given run."""
        run = await self._llm.beta.threads.runs.retrieve(
            thread_id=self._runs[run_id],
            run_id=run_id,
        )
        if run.status in ["cancelled", "expired", "failed"]:
            return f"Error: run {run.status}."
        if run.status == "requires_action":
            return "Error in LLM function call."
        messages = await self._llm.beta.threads.messages.list(
            thread_id=self._runs[run_id],
        )
        return messages.data[0].content[0].text.value

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
        if author not in self._thread_ids:
            await self._spawn_thread(author, name)
        thread_id = self._thread_ids[author]
        await self._llm.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=make_subs(PROMPTS["user"], query, context),
        )
        run = await self._llm.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=self._assistant_id,
        )
        self._runs[run.id] = thread_id
        return run.id


class MilaBot(discord.Client):
    """Implement a Discord bot for interacting with Mila."""

    def __init__(self, mila: Mila, logger: Logger, *args, **kwargs):
        """Initialize MilaBot."""
        super().__init__(*args, **kwargs)
        self._mila = mila
        self._logger = logger
        self._queries = {}

    @tasks.loop(seconds=1)
    async def tick(self) -> None:
        """Update all threads."""
        await self._check_queries()

    async def _check_queries(self) -> None:
        """Check for updates."""
        for task_id in list(self._queries.keys()):
            if await self._mila.check_completion(task_id):
                response = await self._mila.get_response(task_id)
                await self._queries[task_id].edit(content=response)
                self._queries.pop(task_id)

    async def _get_context(self, message: discord.Message):
        """Pull the message history and format it for Mila."""
        context = [
            f"{msg.author.name}: {msg.content}"
            async for msg in message.channel.history(limit=CONTEXT_LIMIT)
        ][::-1]
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
    """Launch MilaBot."""
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
