"""Provide the Mila library."""

import asyncio
import json

from openai import AsyncOpenAI

from lib.logging import LOGGER, logging
from mila.constants import DESCRIPTION, MODEL, NAME
from mila.prompts import PROMPTS

LLM = AsyncOpenAI()


async def get_horoscope(star_sign: str) -> str:
    """Get the horoscope for a given star sign."""
    LOGGER.info("Function called: get_horoscope")
    return f"Your horoscope for {star_sign} is: Memento mori."


async def suggest_feature(
    feature: str,
    category: str,
    implementation: str,
) -> str:
    """Suggest a feature to expand Mila's capabilities."""
    LOGGER.info("Function called: suggest_feature")
    LOGGER.info("- Feature: %s", feature)
    LOGGER.info("- Category: %s", category)
    LOGGER.info("- Implementation: %s", implementation)
    return f"Feature suggestion received: {feature} ({category})."


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
        },
        {
            "name": "suggest_feature",
            "function": suggest_feature,
            "description": (
                "Unable to solve a user's request due to a lack of available"
                + "tools? Suggest a feature to expand Mila's capabilities."
            ),
            "properties": {
                "feature": {
                    "type": "string",
                    "description": "The suggested feature, in plain English.",
                },
                "category": {
                    "type": "string",
                    "description": "A one-word category for the feature.",
                },
                "implementation": {
                    "type": "string",
                    "description": "The proposed feature implementation.",
                },
            },
            "required": ["feature", "category", "implementation"],
        },
    ]

    def __init__(self, logger: logging.Logger):
        """Initialize Mila."""
        self._llm = AsyncOpenAI()
        self._logger = logger
        self._assistant_id = None
        self._thread_ids = {}
        # Mila is async, and can handle multiple threads concurrently,
        # but each thread can only handle one run at a time. (Thanks, OpenAI.)
        self._thread_locks = {}
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
        self._thread_locks[thread.id] = False

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
            complete = True
        elif run.status == "requires_action":
            self._logger.info("Run requires action.")
            for (
                tool_call
            ) in run.required_action.submit_tool_outputs.tool_calls:
                arguments = json.loads(tool_call.function.arguments)
                name = tool_call.function.name
                found = False
                for tool in self._tool_definitions:
                    if tool["name"] == name:
                        found = True
                        if tool["function"]:
                            response = await tool["function"](**arguments)
                            tool_call_id = tool_call.id
                            tool_outputs.append(
                                {
                                    "tool_call_id": tool_call_id,
                                    "output": response,
                                }
                            )
                        else:
                            self._logger.warn(
                                "Undefined function: %s",
                                name,
                            )
                            complete = True
                if not found:
                    self._logger.warn("Undefined tool: %s", name)
                    complete = True
            if tool_outputs:
                self._logger.info("Submitting tool outputs.")
                run = await self._llm.beta.threads.runs.submit_tool_outputs(
                    thread_id=self._runs[run_id],
                    run_id=run_id,
                    tool_outputs=tool_outputs,
                )
        if complete:
            self._thread_locks[self._runs[run_id]] = False
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
        while self._thread_locks[thread_id]:
            await asyncio.sleep(0.1)
        self._thread_locks[thread_id] = True
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
