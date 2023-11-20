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
        self._assistant = LLM.beta.assistants.create(
            instructions=PROMPTS["instructions"],
            name="Mila",
            model=MODEL,
            tools=[
                {
                    "type": "function",
                    "function": {
                        "name": "get_horoscope",
                        "description": "Get the horoscope for a given star sign.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "star_sign": {
                                    "type": "string",
                                    "description": "The star sign to get the horoscope for.",
                                }
                            },
                            "required": ["star_sign"]
                        }
                    }
                }
            ]
        )
        self._logger = logger
        self._tasks = {}

    def _make_subs(self, prompt_list: list, query: str, context: str) -> str:
        """Make substitutions to the query and context."""
        sub_dict = {
            "query": query,
            "context": context,
        }
        for prompt in prompt_list:
            prompt["content"] = prompt["content"].format(**sub_dict)
        return prompt_list

    async def add_task(self, query: str, context: str) -> str:
        """Add a task to Mila."""
        task_id = sha256((query + context).encode("utf-8")).hexdigest()
        self._logger.info("Task %s created. -> %s", task_id, query)
        generator = await LLM.chat.completions.create(
            model=MODEL,
            messages=self._make_subs(PROMPTS.as_list, query, context),
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
        except TypeError:
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
