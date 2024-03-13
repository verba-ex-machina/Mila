"""Provide collections of objects for the Mila Framework."""

from typing import Dict

from mila.base.commands import POWER_WORD_KILL
from mila.base.interfaces import MilaAssistant

ASSISTANTS: Dict[str, MilaAssistant] = {}
COMMANDS = [POWER_WORD_KILL]
