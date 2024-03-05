"""Define global constant values."""

from collections import namedtuple

import openai

TICK = 0.1  # Seconds per tick.
STATES = namedtuple("STATES", "NEW COMPLETE")("NEW", "COMPLETE")
LLM = openai.AsyncOpenAI()
