"""Define global constants and objects."""

from collections import namedtuple

import openai

TICK = 0.1  # Seconds per tick.
STATES = namedtuple("STATES", ["NEW", "OUTBOUND", "PROCESSING", "COMPLETE"])(
    *["NEW", "OUTBOUND", "PROCESSING", "COMPLETE"]
)
LLM = openai.AsyncOpenAI()
