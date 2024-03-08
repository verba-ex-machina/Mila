"""Provide tests for the MilaProc class."""

from dataclasses import dataclass
from typing import List

import pytest

from mila import MilaProc
from mila.base.interfaces import TaskIO
from mila.base.types import MilaTask
from mila.module.fake import FakeDB, FakeIO

from .common import make_task


@dataclass
class Results:
    """Results of the test."""

    received: bool = False
    sent: bool = False
    initialized: bool = False
    torn_down: bool = False


RESULTS = Results()


class DemoIO(TaskIO):
    """Provide a demo IO handler for testing the MilaProc class."""

    async def setup(self) -> None:
        """Set up the Demo IO handler."""
        RESULTS.initialized = True

    async def teardown(self) -> None:
        """Tear down the Demo IO handler."""
        RESULTS.torn_down = True

    async def recv(self) -> List[MilaTask]:
        """Receive a task."""
        if not RESULTS.received:
            # The first message will be to FakeIO, which will echo it back.
            RESULTS.received = True
            task = make_task()
            task.source = {
                "handler": "DemoIO",
            }
            task.destination = {
                "handler": "FakeIO",
            }
            return [task]
        # If the test message was already sent, send an exit command.
        task = make_task()
        task.content = "exit"
        return [task]

    async def send(self, task_list: List[MilaTask]) -> None:
        """Send a task."""
        for task in task_list:
            # Ensure we're the intended recipient.
            if task.destination["handler"] == "DemoIO":
                RESULTS.sent = True


@pytest.mark.asyncio
async def test_milaproc():
    """Test the MilaProc class."""
    async with MilaProc(db=FakeDB, task_io_handlers=[DemoIO, FakeIO]) as mila:
        await mila.run()
    # Ensure the DemoIO handler was setup and torn down.
    # This tests the MilaProc task IO handler lifecycle.
    assert RESULTS.initialized
    assert RESULTS.torn_down
    # Ensure the DemoIO handler received and sent a message.
    # This tests the MilaProc task routing logic.
    assert RESULTS.received
    assert RESULTS.sent
