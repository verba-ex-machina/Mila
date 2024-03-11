"""Provide common functions across tests."""

from mila.base.types import MilaTask


def make_task(data: str = "None") -> MilaTask:
    """Make a MilaTask."""
    task = MilaTask(context="context", content="content", meta={"data": data})
    return task
