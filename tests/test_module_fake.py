"""Test the fake module."""

import pytest

from mila.base.constants import STATES
from mila.base.types import MilaTask
from mila.module.fake import FakeIO, FakeStorage

from .common import make_task


@pytest.mark.asyncio
async def test_fake_io():
    """Test the FakeIO class."""
    async with FakeIO() as fake_io:

        def copy_src_to_dest(task: MilaTask) -> MilaTask:
            """Move source to destination."""
            task = task.copy()
            task.destination = task.source.copy()
            task.source["handler"] = FakeIO.__name__
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


@pytest.mark.asyncio
async def test_fake_storage():
    """Test the FakeStorage class."""
    fake_storage = FakeStorage()
    task = make_task("task1")
    # Create
    task_id = await fake_storage.create(task)
    with pytest.raises(KeyError):
        await fake_storage.create(task)
    # Read
    assert await fake_storage.read(task_id) == task
    with pytest.raises(KeyError):
        await fake_storage.read("fake_id")
    # Update
    task.context = "new_context"
    await fake_storage.update(task_id, task)
    task = await fake_storage.read(task_id)
    assert task.context == "new_context"
    with pytest.raises(KeyError):
        await fake_storage.update("fake_id", task)
    # Delete
    await fake_storage.delete(task_id)
    with pytest.raises(KeyError):
        await fake_storage.read(task_id)
    with pytest.raises(KeyError):
        await fake_storage.update(task_id, task)
    with pytest.raises(KeyError):
        await fake_storage.delete(task_id)
    with pytest.raises(KeyError):
        await fake_storage.delete("fake_id")
    # By State
    task1 = make_task("task1")
    task2 = make_task("task2")
    task1.state = STATES.COMPLETE
    await fake_storage.create(task1)
    await fake_storage.create(task2)
    assert await fake_storage.by_state(state=STATES.NEW) == [task2]
    assert await fake_storage.by_state(state=STATES.COMPLETE) == [task1]
