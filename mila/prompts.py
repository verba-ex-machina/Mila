"""Provide prompts for Mila."""


from mila.constants import DESCRIPTION, PROMPT_PATH


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
        with open(f"{PROMPT_PATH}{name}.txt", "r", encoding="utf-8") as file:
            return self._make_subs(file.read().strip())

    @property
    def as_list(self) -> list:
        """Return the prompts formatted as a list."""
        return [
            {"role": name, "content": self[name]}
            for name in [
                "system",
                "user",
            ]
        ]


PROMPTS = Prompts()
