"""Provide the Mila library."""

import asyncio
import hashlib
import json

import openai

from mila import config
from mila.logging import logging
from mila.prompts import PROMPTS
from mila.tools import TOOLS


def assistant_hash() -> str:
    """Get the hash of the current assistant."""
    return hashlib.sha256(
        json.dumps(
            {
                "instructions": PROMPTS["system"],
                "tools": TOOLS.definitions,
                "model": config.MODEL,
                "version": config.VERSION,
            }
        ).encode("utf-8")
    ).hexdigest()


class Mila:
    """Represent the Mila assistant."""

    def __init__(self, logger: logging.Logger):
        """Initialize Mila."""
        self._llm = openai.AsyncOpenAI()
        self._logger = logger
        self._assistant = None
        self._thread_ids = {}
        # Mila is async, and can handle multiple threads concurrently,
        # but each thread can only handle one run at a time. (Thanks, OpenAI.)
        self._thread_locks = {}
        self._runs = {}

    async def _spawn_assistant(self) -> openai.types.beta.Assistant:
        """Link or spawn an assistant for the bot."""
        assistants = await self._llm.beta.assistants.list(limit=100)
        for assistant in assistants.data:
            if assistant.name == config.NAME:
                self._logger.info("Assistant found.")
                if "hash" not in assistant.metadata.keys() or assistant.metadata["hash"] != assistant_hash():
                    await self._llm.beta.assistants.update(
                        assistant.id,
                        instructions=PROMPTS["system"],
                        tools=TOOLS.definitions,
                        model=config.MODEL,
                        metadata={
                            "hash": assistant_hash(),
                        },
                    )
                    self._logger.info("Assistant updated.")
                return assistant
        self._logger.info("No assistants found. New assistant spawned.")
        return await self._llm.beta.assistants.create(
            instructions=PROMPTS["system"],
            name=config.NAME,
            model=config.MODEL,
            tools=TOOLS.definitions,
            metadata={
                "hash": assistant_hash(),
            },
        )

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
                for tool in TOOLS.definitions:
                    if tool["function"]["name"] == name:
                        found = True
                        function = TOOLS.get(name)
                        if function:
                            response = await function(
                                **arguments,
                            )
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
        if not self._assistant:
            self._assistant = await self._spawn_assistant()
        if author not in self._thread_ids:
            await self._spawn_thread(author, name)
        thread_id = self._thread_ids[author]
        while self._thread_locks[thread_id]:
            await asyncio.sleep(0.1)
        self._thread_locks[thread_id] = True
        await self._llm.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=PROMPTS.format(
                name="user",
                sub_dict={
                    "context": context,
                    "query": query,
                },
            ),
        )
        run = await self._llm.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=self._assistant.id,
        )
        self._runs[run.id] = thread_id
        return run.id
