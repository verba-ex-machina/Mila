"""Provide tests for the MilaProc class."""

from dataclasses import dataclass
from typing import List

import mila
from mila.base.commands import POWER_WORD_KILL
from mila.base.interfaces import TaskIO
from mila.base.types import Task
from mila.modules.fake import FakeIO, FakeLLM, FakeTracker
from tests.common import make_task


@dataclass
class Results:
    """Results of the test."""

    received: bool = False
    sent: bool = False
    set_up: bool = False
    torn_down: bool = False


RESULTS = Results()


class DemoIO(TaskIO):
    """Provide a demo IO handler for testing the MilaProc class."""

    async def setup(self) -> None:
        """Set up the Demo IO handler."""
        RESULTS.set_up = True

    async def teardown(self) -> None:
        """Tear down the Demo IO handler."""
        RESULTS.torn_down = True

    async def recv(self) -> List[Task]:
        """Receive a task."""
        if not RESULTS.received:
            RESULTS.received = True
            task = make_task()
            task.src.handler = "DemoIO"
            task.dst.handler = "FakeIO"
            return [task]
        return [POWER_WORD_KILL]

    async def send(self, task_list: List[Task]) -> None:
        """Send a task."""
        for task in task_list:
            if task == POWER_WORD_KILL:
                continue
            if task.dst.handler == "DemoIO":
                RESULTS.sent = True


def test_mila():
    """Test the Mila Framework."""
    mila.run(
        llm=FakeLLM,
        task_io_handlers=[DemoIO, FakeIO],
        task_tracker=FakeTracker,
    )
    assert RESULTS.set_up
    assert RESULTS.received
    assert RESULTS.sent
    assert RESULTS.torn_down
