"""Test the FakeIO class."""

import pytest

from mila.io import FakeIO

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
