"""Provide Mila Framework modules."""

from typing import List

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from mila.assistants import ASSISTANTS
from mila.base.constants import LLM, STATES
from mila.base.interfaces import TaskIO, TaskStorage
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


class MilaStorage(TaskStorage):
    """Mila Framework storage class."""

    initialized: bool = False
    engine: AsyncEngine

    async def _add_to_db(self, task: MilaTask) -> str:
        """Add a task to the database."""
        # pylint: disable=fixme
        # TODO: Implement this method.
        return hash(task)

    async def _setup(self) -> None:
        """Initialize the storage channel."""
        self.engine = create_async_engine(
            "sqlite+aiosqlite:///:memory:", echo=True
        )
        self.initialized = True

    async def _spawn_run(self, assistant_id, thread):
        """Spawn a new run for the given assistant and thread."""
        run = await LLM.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant_id,
        )
        return run

    async def _spawn_thread(self, task):
        """Spawn a new thread for the given task."""
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
        return thread

    # pylint: disable=no-self-argument
    def db_required(function: callable):
        """Ensure that the database is initialized when needed."""

        async def wrapper(self: "MilaStorage", *args, **kwargs):
            """Initialize the database if needed."""
            # pylint: disable=protected-access
            # pylint: disable=not-callable
            if not self.initialized:
                await self._setup()
            return await function(self, *args, **kwargs)

        return wrapper

    @db_required
    async def create(self, task: MilaTask) -> str:
        """Create a task in the storage channel."""
        try:
            assistant = ASSISTANTS[task.assignee].spawn()
        except KeyError as exc:
            raise ValueError(
                f"Failed to create task: Unknown assistant {task.assignee}"
            ) from exc
        assistant_id = await assistant.id()
        thread = await self._spawn_thread(task)
        run = await self._spawn_run(assistant_id, thread)
        task.state = STATES.PROCESSING
        task.meta["assistant_id"] = assistant_id
        task.meta["thread_id"] = thread.id
        task.meta["run_id"] = run.id
        return await self._add_to_db(task)

    @db_required
    async def read(self, task_id: str) -> MilaTask:
        """Read a task from the storage channel."""

    @db_required
    async def update(self, task_id: str, task: MilaTask) -> None:
        """Update a task in the storage channel."""

    @db_required
    async def delete(self, task_id: str) -> None:
        """Delete a task from the storage channel."""

    @db_required
    async def by_state(self, state: str) -> List[MilaTask]:
        """Retrieve tasks by state from the storage channel."""
        return []


class MilaIO(TaskIO):
    """Mila Framework I/O handler class."""

    task_storage: TaskStorage

    async def recv(self) -> List[MilaTask]:
        """Receive tasks from the I/O handler."""
        return await self.task_storage.by_state(state=STATES.OUTBOUND)

    async def send(self, task_list: List[MilaTask]) -> None:
        """Send tasks to the I/O handler."""
        for task in task_list:
            await self.task_storage.create(task)

    async def setup(self) -> None:
        """Prepare the I/O handler."""
        self.task_storage = MilaStorage()
