"""Provide prompts for Mila."""

from mila.constants import DESCRIPTION

_PATH = "mila/prompts/"


class Prompts:
    """Represent the library of Mila's prompts."""

    _subs = {
        # Replace values in prompt files on-the-fly.
        "DESCRIPTION": DESCRIPTION,
    }

    def _make_subs(self, content: str) -> str:
        """Make substitutions in a string."""
        for key, value in self._subs.items():
            content = content.replace(f"{{{key}}}", value)
        return content

    def __getitem__(self, name: str) -> str:
        """Get a prompt by name."""
        with open(f"{_PATH}{name}.txt", "r", encoding="utf-8") as file:
            return self._make_subs(file.read().strip())


PROMPTS = Prompts()
