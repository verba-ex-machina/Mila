"""Provide access to the OpenAI Threads feature."""

from mila.llm import LLM
from mila.prompts import PROMPTS
from mila.runs import Run


class Thread:
    """Provide an abstraction for the OpenAI Threads API."""

    def __init__(
        self,
        assistant_id: str,
        context: str,
        query: str,
    ):
        """Initialize the Thread."""
        self._thread = None
        self._run = None
        self._assistant_id = assistant_id
        self._context = context
        self._query = query

    async def _spawn_thread(self):
        """Spawn a new thread."""
        self._thread = await LLM.beta.threads.create(
            messages=[
                {
                    "role": "user",
                    "content": PROMPTS.format(
                        name="user",
                        sub_dict={
                            "context": self._context,
                            "query": self._query,
                        },
                    ),
                }
            ],
        )
        self._run = Run(
            thread_id=self._thread.id,
            assistant_id=self._assistant_id,
        )

    async def id(self) -> str:
        """Get the ID of the thread."""
        if not self._thread:
            await self._spawn_thread()
        return self._thread.id

    async def check(self) -> bool:
        """Check whether a query run is complete."""
        return await self._run.check()

    async def response(self) -> str:
        """Retrieve the final response from a given run."""
        return await self._run.response()
