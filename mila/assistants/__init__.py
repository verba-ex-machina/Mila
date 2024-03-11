"""Manage Assistants within the Mila Framework."""

import mila.assistants.overmind
from mila.base.collections import ASSISTANTS


def available():
    """List all available assistants."""
    return ASSISTANTS.values()
