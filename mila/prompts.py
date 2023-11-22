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
        with open(f"{PROMPT_PATH}{name}.txt", "r", encoding="utf-8") as file:
            return file.read().strip().format(**self._global_subs)

    def format(self, name: str, sub_dict: dict = None) -> str:
        """Get a prompt by name and format it."""
        return self[name] if not sub_dict else self[name].format(**sub_dict)

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
