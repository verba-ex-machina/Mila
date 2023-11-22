"""Define Mila's configuration."""

import logging

NAME = "Mila"
DESCRIPTION = "the Mindful, Interactive Lifestyle Assistant"
LOG_LEVEL = logging.DEBUG
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
MODEL = "gpt-3.5-turbo-16k"
PROMPT_PATH = "mila/prompts/"
