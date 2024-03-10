"""Provide common functions across tests."""

from mila.base.constants import STATES
from mila.base.types import MilaTask


def make_task(data: str = "None") -> MilaTask:
    """Make a MilaTask."""
    return MilaTask(
        context="context",
        content="prompt",
        source={"handler": data},
        state=STATES.NEW,
    )
