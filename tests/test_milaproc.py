"""Provide tests for the MilaProc class."""

from dataclasses import dataclass
from typing import List

import pytest

from mila import MilaProc
from mila.base.commands import POWER_WORD_KILL
from mila.base.interfaces import TaskIO
from mila.base.types import MilaTask
from mila.io.fake import FakeIO
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

    async def recv(self) -> List[MilaTask]:
        """Receive a task."""
        if not RESULTS.received:
            RESULTS.received = True
            task = make_task()
            task.src.handler = "DemoIO"
            task.dst.handler = "FakeIO"
            return [task]
        return [POWER_WORD_KILL]

    async def send(self, task_list: List[MilaTask]) -> None:
        """Send a task."""
        for task in task_list:
            if task == POWER_WORD_KILL:
                continue
            if task.dst.handler == "DemoIO":
                RESULTS.sent = True


@pytest.mark.asyncio
async def test_milaproc():
    """Test the MilaProc class."""
    async with MilaProc(task_io_handlers=[DemoIO, FakeIO]) as mila:
        assert RESULTS.set_up
        await mila.run()
        assert RESULTS.received
        assert RESULTS.sent
        assert not RESULTS.torn_down
    assert RESULTS.torn_down
