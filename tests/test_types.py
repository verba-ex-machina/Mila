"""Test mila.types."""

import pytest

from mila.types import MilaTask


def test_mila_task():
    """Test the MilaTask class."""
    task1 = MilaTask(
        context="test", prompt="test", meta={"test": "test"}, id="test"
    )
    task2 = MilaTask(
        context="test", prompt="test", meta={"test": "test"}, id="test"
    )
    assert task1 == task2
    assert task1.timestamp != task2.timestamp
    task3 = MilaTask(
        context="test",
        prompt="test",
        meta={"test": "test"},
        timestamp="2021-01-01T00:00:00.000000Z",
    )
    task3.validate()
    assert task1 != task3
    task5 = MilaTask(context="test", prompt="test")
    assert len(sorted([task1, task3, task2, task5])) == 4
    assert task5.id is not None
    assert task5.timestamp is not None
    assert task5.meta is not None
    task6 = MilaTask(context="test", prompt="test", timestamp="badtimestamp")
    with pytest.raises(ValueError):
        task6.validate()
