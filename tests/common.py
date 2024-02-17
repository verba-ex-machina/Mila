"""Provide common functions across tests."""

from mila.base.types import MilaTask


def make_task() -> MilaTask:
    """Make a MilaTask."""
    return MilaTask(
        context="context",
        content="prompt",
        meta={"meta": "data"},
    )
