"""Test the fake module."""

import pytest

from mila.base.types import MilaTask
from mila.module.fake import FakeIO

from .common import make_task


@pytest.mark.asyncio
async def test_fake_io():
    """Test the FakeIO class."""
    async with FakeIO() as fake_io:

        def copy_src_to_dest(task: MilaTask) -> MilaTask:
            """Copy source to destination."""
            task.destination = task.source.copy()
            return task

        # Phase 1
        assert await fake_io.recv() == []
        task = make_task()
        await fake_io.send([task])
        assert await fake_io.recv() == [copy_src_to_dest(task)]
        assert await fake_io.recv() == []
        # Phase 2
        task1 = make_task("task1")
        task2 = make_task("task2")
        await fake_io.send([task1])
        await fake_io.send([task1, task2])
        assert await fake_io.recv() == [
            copy_src_to_dest(task1),
            copy_src_to_dest(task2),
        ]
        assert await fake_io.recv() == []
