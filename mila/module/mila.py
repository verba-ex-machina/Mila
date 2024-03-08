"""Provide Mila Framework modules."""

import asyncio
from typing import List

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from mila.assistants import ASSISTANTS
from mila.base.constants import LLM, STATES
from mila.base.interfaces import TaskIO
from mila.base.types import MilaTask

MSG_FORMAT = """
A new request has arrived. Here is the context:

```
{context}
```

Here is the request:

> {query}

Please respond appropriately to the user's request, per the terms of your
instructions. Use whatever tools are at your disposal to provide the best
possible response. If you need help, you can ask other assistants for their
input by delegating tasks to them. If you encounter problems, report them
in your response.
"""


class MilaIO(TaskIO):
    """Mila Framework I/O handler class."""

    tasks: List[MilaTask] = []
    engine: AsyncEngine
    initialized: bool = False

    async def _setup(self) -> None:
        """Initialize the storage channel."""
        self.engine = create_async_engine(
            "sqlite+aiosqlite:///:memory:", echo=True
        )
        self.initialized = True

    @staticmethod
    def db_required(function: callable):
        """Ensure that the database is initialized when needed."""

        async def wrapper(self: "MilaIO", *args, **kwargs):
            """Initialize the database if needed."""
            # pylint: disable=protected-access
            # pylint: disable=not-callable
            if not self.initialized:
                await self._setup()
            return await function(self, *args, **kwargs)

        return wrapper

    @db_required
    async def recv(self) -> List[MilaTask]:
        """Receive tasks from the I/O handler."""
        outbound = [
            task for task in self.tasks if task.state == STATES.OUTBOUND
        ]
        self.tasks = [
            task for task in self.tasks if task.state != STATES.OUTBOUND
        ]
        return outbound

    @db_required
    async def send(self, task_list: List[MilaTask]) -> None:
        """Send tasks to the I/O handler."""
        await asyncio.gather(*[self._process_task(task) for task in task_list])

    async def _process_task(self, task: MilaTask) -> None:
        """Process a single task."""
        # Consider moving this to within the assistants themselves.
        try:
            assistant = ASSISTANTS[task.assignee].spawn()
        except KeyError as exc:
            raise ValueError(
                f"Failed to send task: Unknown assistant {task.assignee}"
            ) from exc
        assistant_id = await assistant.id()
        thread = await LLM.beta.threads.create(
            messages=[
                {
                    "role": "user",
                    "content": (
                        " ".join(MSG_FORMAT.strip().split("\n")).format(
                            context=task.context, query=task.content
                        )
                    ),
                }
            ],
        )
        run = await LLM.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant_id,
        )
        task.state = STATES.PROCESSING
        task.meta["assistant_id"] = assistant_id
        task.meta["thread_id"] = thread.id
        task.meta["run_id"] = run.id
        self.tasks.append(task)
