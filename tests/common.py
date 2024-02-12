"""Provide common functions across tests."""

from mila.base.types import MilaTask


def make_task() -> MilaTask:
    """Make a MilaTask."""
    return MilaTask(
        context="context",
        prompt="prompt",
        response="response",
        meta={"meta": "data"},
    )
