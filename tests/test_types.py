"""Test Mila types."""

from .common import make_task


def test_mila_task():
    """Test the MilaTask class."""
    task = make_task()
    hash(task)
    task2 = task.copy()
    assert task == task2
    task2.destination.handler = "data2"
    assert task != task2
