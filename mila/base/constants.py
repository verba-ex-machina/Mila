"""Define global constant values."""

from collections import namedtuple

TICK = 0.1  # Seconds per tick.
STATES = namedtuple("STATES", "NEW COMPLETE")("NEW", "COMPLETE")
