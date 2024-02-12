"""Test the FakeIO class."""

import pytest

from mila.module.fake import FakeIO, FakeStorage

from .common import make_task


@pytest.mark.asyncio
async def test_fake_io():
    """Test the FakeIO class."""
    fake_io = FakeIO()
    task = make_task()
    assert await fake_io.recv() is None
    await fake_io.send(task)
    assert await fake_io.recv() == task
    assert await fake_io.recv() is None
    await fake_io.send(task)
    await fake_io.send(task)
    assert await fake_io.recv() == task
    assert await fake_io.recv() is None


@pytest.mark.asyncio
async def test_fake_storage():
    """Test the FakeStorage class."""
    fake_storage = FakeStorage()
    task = make_task()
    task2 = make_task()
    task2.meta["meta"] = "data2"
    task1_id = await fake_storage.create(task)
    assert await fake_storage.read(task1_id) == task
    task2_id = await fake_storage.create(task)
    assert task2_id == task1_id
    task2_id = await fake_storage.create(task2)
    assert task2_id != task1_id
    assert await fake_storage.read(task2_id) == task2
    task.context = "context2"
    await fake_storage.update(task1_id, task)
    task = await fake_storage.read(task1_id)
    assert task.context == "context2"
    await fake_storage.delete(task1_id)
    assert await fake_storage.read(task1_id) is None
    assert await fake_storage.read(task2_id) == task2
    await fake_storage.delete(task2_id)
    assert await fake_storage.read(task2_id) is None
    assert await fake_storage.read("fake_id") is None
    with pytest.raises(KeyError):
        await fake_storage.update("fake_id", task)
    with pytest.raises(KeyError):
        await fake_storage.delete("fake_id")
