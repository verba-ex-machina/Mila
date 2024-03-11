"""Provide common functions across tests."""

from mila.base.types import MilaTask


def make_task(data: str = "None") -> MilaTask:
    """Make a MilaTask."""
    task = MilaTask(context="context", content=data)
    return task
