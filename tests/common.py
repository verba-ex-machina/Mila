"""Provide common functions across tests."""

from mila.base.types import MilaTask, MilaTaskMeta, MilaTaskStates


def make_task(data: str = "None") -> MilaTask:
    """Make a MilaTask."""
    return MilaTask(
        context="context",
        content="prompt",
        meta=MilaTaskMeta(
            source={"handler": data},
            destination={},
            state=MilaTaskStates.NEW,
        ),
    )
