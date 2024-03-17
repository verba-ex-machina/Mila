"""Provide the Fake module."""

from typing import Dict, List

from mila.base.interfaces import MilaAssistant, MilaLLM, TaskIO, TaskTracker
from mila.base.types import AssistantDefinition, MilaTask


class FakeAssistant(MilaAssistant):
    """Define the FakeAssistant class."""

    _fakeio: TaskIO

    def __init__(self, definition: AssistantDefinition) -> None:
        """Initialize the FakeAssistant."""
        super().__init__(definition)
        self._fakeio = FakeIO()

    async def send(self, task_list: List[MilaTask]) -> None:
        """Send a list of tasks to the FakeAssistant."""
        await self._fakeio.send(task_list)

    async def recv(self) -> List[MilaTask]:
        """Receive all queued tasks from the FakeAssistant."""
        return await self._fakeio.recv()


class FakeIO(TaskIO):
    """Implement a fake TaskIO interface."""

    tasks: List[MilaTask] = []

    async def recv(self) -> List[MilaTask]:
        """Receive all queued tasks from FakeIO."""
        tasks = [task.copy() for task in self.tasks]
        self.tasks.clear()
        for task in tasks:
            task.dst = task.src.copy()
        return tasks

    async def send(self, task_list: List[MilaTask]) -> None:
        """Send a list of tasks to FakeIO."""
        for task in task_list:
            if task not in self.tasks:
                self.tasks.append(task.copy())

    async def setup(self) -> None:
        """Prepare the FakeIO channel."""
        self.tasks.clear()


class FakeLLM(MilaLLM):
    """Fake LLM implementation."""

    async def get_assistant(
        self, definition: AssistantDefinition
    ) -> MilaAssistant:
        """Return a fake assistant."""
        return FakeAssistant(definition)

    async def setup(self) -> None:
        """Prepare the LLM."""

    async def teardown(self) -> None:
        """Teardown the LLM."""


class FakeTracker(TaskTracker):
    """Fake task tracker."""

    _tasks: Dict[str, MilaTask]

    def __init__(self):
        """Initialize the FakeTracker."""
        self._tasks = {}

    async def create(self, task: MilaTask) -> str:
        """Add a task to the tracker."""
        self._tasks[hash(task)] = task
        return hash(task)

    async def read(self, task_id: str) -> MilaTask:
        """Get a task from the tracker."""
        return self._tasks[task_id]

    async def update(self, task_id: str, task: MilaTask) -> None:
        """Update a task in the tracker."""
        if task_id in self._tasks:
            self._tasks[task_id] = task
        else:
            raise KeyError(f"Task {task_id} not found.")

    async def delete(self, task_id: str) -> None:
        """Drop a task from the tracker."""
        del self._tasks[task_id]

    async def by_state(self, state: str) -> List[MilaTask]:
        """Get tasks by state."""
        return [
            task for task in self._tasks.values() if task.meta.state == state
        ]
