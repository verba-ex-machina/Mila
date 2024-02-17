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
    task = make_task()
    task2 = make_task()
    task2.meta["meta"] = "data2"
    task1_id = await fake_storage.create(task)
    task1_duplicate_id = await fake_storage.create(task)
    assert task1_duplicate_id == task1_id
    task2_id = await fake_storage.create(task2)
    task.context = "context2"
    await fake_storage.update(task1_id, task)
    task = await fake_storage.read(task1_id)
    await fake_storage.delete(task1_id)
    assert task.context == "context2"
    assert await fake_storage.read(task1_id) is None
    assert await fake_storage.read(task2_id) == task2
    assert await fake_storage.read("fake_id") is None
    with pytest.raises(KeyError):
        await fake_storage.update("fake_id", task)
    with pytest.raises(KeyError):
        await fake_storage.delete("fake_id")
