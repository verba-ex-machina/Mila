"""MilaBot logging module."""

import logging
from mila.constants import LOG_FORMAT, LOG_LEVEL, NAME

# Create a logger for the Mila bot, used by both the Discord and AI modules.
LOGGER = logging.getLogger(NAME)
LOGGER.setLevel(LOG_LEVEL)

# Create a file handler for the logger.
fh = logging.FileHandler(f"logs/{NAME}.log")
fh.setLevel(LOG_LEVEL)

# Create a stream handler for the logger.
sh = logging.StreamHandler()
sh.setLevel(LOG_LEVEL)

# Create a formatter for the logger.
formatter = logging.Formatter(
    LOG_FORMAT,
)

# Add the formatter to the handlers.
fh.setFormatter(formatter)
sh.setFormatter(formatter)

# Add the handlers to the logger.
LOGGER.addHandler(fh)
LOGGER.addHandler(sh)