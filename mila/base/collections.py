"""Provide collections of objects for the Mila Framework."""

from typing import Dict

from mila.base.commands import POWER_WORD_KILL
from mila.base.types import AssistantDefinition

ASSISTANTS: Dict[str, AssistantDefinition] = {}
COMMANDS = [POWER_WORD_KILL]
