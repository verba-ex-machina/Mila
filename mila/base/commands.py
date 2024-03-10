"""Define global commands for the Mila Framework."""

from mila.base.types import MilaTask


POWER_WORD_KILL = MilaTask(
    content="TERMINATE",
    context="COMMAND",
)

COMMANDS = [POWER_WORD_KILL]