"""Test Mila types."""

import json
from dataclasses import asdict

from .common import make_task


def test_mila_task():
    """Test the MilaTask class."""
    task = make_task()
    assert repr(task) == json.dumps(asdict(task))
    assert bytes(task) == repr(task).encode()
    assert hash(task) == hash(str(task))
    task2 = task.copy()
    assert task == task2
    task2.destination["handler"] = "data2"
    assert task != task2
