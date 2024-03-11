"""Test Mila types."""

from tests.common import make_task


def test_mila_task():
    """Test the MilaTask class."""
    task = make_task()
    hash(task)
    task2 = task.copy()
    assert task == task2
    task2.dst.handler = "data2"
    assert task != task2
