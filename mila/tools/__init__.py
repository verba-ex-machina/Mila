"""Provide a suite of tools for the toolkit."""

from mila.tools import util


class Tool:
    """Represent a single tool in Mila's toolset."""

    def __init__(self, tool: callable):
        """Initialize the tool."""
        self._tool = tool

    @property
    def definition(self) -> dict:
        """Get the tool definition."""
        return {
            "type": "function",
            "function": {
                "name": self._tool.__name__,
                "description": self._tool.__doc__,
                "parameters": {
                    "type": "object",
                    "properties": self._tool.properties,
                    "required": self._tool.required,
                },
            },
        }

    @property
    def function(self) -> callable:
        """Get the tool function."""
        return self._tool


class Tools:
    """Represent Mila's available toolset."""

    def __init__(self, toolkits: list):
        """Initialize the toolset."""
        self._tools = []
        for toolkit in toolkits:
            contents = dir(toolkit)
            for item in contents:
                element = getattr(toolkit, item)
                if callable(element) and hasattr(element, "properties"):
                    self._tools.append(Tool(element))

    @property
    def definitions(self) -> list:
        """Get the tool definitions."""
        return [tool.definition for tool in self._tools]

    def get(self, name: str) -> callable:
        """Get a tool by name."""
        for tool in self._tools:
            if tool.definition["function"]["name"] == name:
                return tool.function
        raise ValueError(f"No tool named {name} exists.")


TOOLS = Tools(
    [
        util,
    ]
)
