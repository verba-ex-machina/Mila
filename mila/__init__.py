"""Provide the Mila library."""

import logging
from hashlib import sha256

from openai import AsyncOpenAI
from openai.types.chat.chat_completion import ChatCompletion

from mila.constants import DESCRIPTION, MODEL
from mila.prompts import PROMPTS

LLM = AsyncOpenAI()


class Mila:
    """Represent Mila."""

    class MilaTask:
        """Represent a single request to the Mila AI."""

        def __init__(
            self,
            query: str,
            context: str,
            generator: ChatCompletion,
        ):
            """Initialize the task."""
            self.query = query
            self.context = context
            self.generator = generator
            self.response = ""

    def __init__(self, logger: logging.Logger):
        """Initialize Mila."""
        self.description = DESCRIPTION
        self._logger = logger
        self._tasks = {}

    async def add_task(self, query: str, context: str) -> str:
        """Add a task to Mila."""
        task_id = sha256((query + context).encode("utf-8")).hexdigest()
        self._logger.info("Task %s created. -> %s", task_id, query)
        generator = await LLM.chat.completions.create(
            model=MODEL,
            messages=PROMPTS.as_list,
            stream=True,
        )
        self._tasks[task_id] = self.MilaTask(query, context, generator)
        return task_id

    async def check(self, task_id: str) -> bool:
        """Check whether the task is complete."""
        try:
            task = self._tasks[task_id]
            # Retrieve the next chunk of text.
            chunk = await task.generator.__anext__()
            task.response += chunk.choices[0].delta.content
        except (TypeError, StopAsyncIteration):
            self._logger.info("Task %s completed.", task_id)
            return True
        except KeyError as exc:
            self._logger.warning("Task %s not found.", task_id)
            raise KeyError from exc
        return False

    def drop_task(self, task_id: str) -> None:
        """Drop a task."""
        del self._tasks[task_id]

    def get_response(self, task_id: str) -> str:
        """Get the response to a task."""
        return self._tasks[task_id].response
