"""Test the fake module."""

import pytest

from mila.module.fake import FakeIO, FakeStorage

from .common import make_task


@pytest.mark.asyncio
async def test_fake_io():
    """Test the FakeIO class."""
    async with FakeIO() as fake_io:
        task = make_task()
        assert await fake_io.recv() == []
        await fake_io.send(task)
        assert await fake_io.recv() == [task]
        assert await fake_io.recv() == []
        await fake_io.send(task)
        task2 = make_task()
        task2.meta["meta"] = "data2"
        await fake_io.send(task)
        await fake_io.send(task2)
        assert await fake_io.recv() == [task, task2]
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
