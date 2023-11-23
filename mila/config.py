"""Define Mila's configuration."""

import logging

# Metadata
VERSION = "0.3.0"

# Identity
NAME = "Mila"
DESCRIPTION = "the Mindful, Interactive Lifestyle Assistant"

# LLM Settings
MODEL = "gpt-3.5-turbo-16k"
PROMPT_PATH = "mila/prompts/"

# Logging
LOG_LEVEL = logging.DEBUG
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
