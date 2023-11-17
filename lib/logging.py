"""MilaBot logging module."""

import logging

# Create a logger for the Mila bot, used by both the Discord and AI modules.
logger = logging.getLogger("mila")
logger.setLevel(logging.DEBUG)

# Create a file handler for the logger.
fh = logging.FileHandler("logs/mila.log")
fh.setLevel(logging.DEBUG)

# Create a stream handler for the logger.
sh = logging.StreamHandler()
sh.setLevel(logging.INFO)

# Create a formatter for the logger.
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Add the formatter to the handlers.
fh.setFormatter(formatter)
sh.setFormatter(formatter)

# Add the handlers to the logger.
logger.addHandler(fh)
logger.addHandler(sh)