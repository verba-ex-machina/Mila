"""Test mila.types."""

import json

from mila.types import MilaTask


def test_mila_task():
    """Test the MilaTask class."""
    task = MilaTask(
        context="context",
        prompt="prompt",
        response="response",
        meta={"meta": "data"},
    )
    task_as_dict = {
        "context": "context",
        "prompt": "prompt",
        "response": "response",
        "meta": {"meta": "data"},
    }
    assert repr(task) == json.dumps(task_as_dict)
    assert bytes(task) == repr(task).encode()
    assert hash(task) == hash(str(task))
    task2 = MilaTask(
        context="context",
        prompt="prompt",
        response="response",
        meta={"meta": "data"},
    )
    assert task == task2
    task2.meta["meta"] = "data2"
    assert task != task2
