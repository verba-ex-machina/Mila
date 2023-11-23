"""Provide prompts for Mila."""


from mila.config import DESCRIPTION, NAME, PROMPT_PATH


class Prompts:
    """Represent the library of Mila's prompts."""

    _global_subs = {
        "name": NAME,
        "description": DESCRIPTION,
    }

    def __getitem__(self, name: str) -> str:
        """Get a prompt by name."""
        return self._load_prompt(name).format(**self._global_subs)

    def _load_prompt(self, name: str) -> str:
        """Read a prompt file."""
        with open(f"{PROMPT_PATH}{name}.txt", "r", encoding="utf-8") as file:
            return file.read().strip()

    def format(self, name: str, sub_dict: dict) -> str:
        """Get a prompt by name and format it."""
        sub_dict.update(self._global_subs)
        return self._load_prompt(name).format(**sub_dict)


PROMPTS = Prompts()
