"""Test Mila types."""

import json
from typing import Optional

from mila.base.types import AssistantDefinition, MilaTool, ToolProperty
from tests.common import make_task, make_tool


def test_mila_task():
    """Test the MilaTask class."""
    task = make_task()
    hash(task)
    task2 = task.copy()
    assert task == task2
    task2.dst.handler = "data2"
    assert task != task2


def test_mila_tool():
    """Test the MilaTool class."""

    def test_function(a: str = "test", b: Optional[int] = None) -> bool:
        """A function which always returns true."""
        return a or b or 1

    tool = MilaTool(
        name="test tool",
        function=test_function,
        properties=[
            ToolProperty(
                name="a",
                type="string",
                description="a test string",
            ),
            ToolProperty(
                name="b",
                type="integer",
                description="a test integer",
            ),
        ],
        required=["a"],
    )
    assert tool.definition == {
        "type": "function",
        "function": {
            "name": "test tool",
            "description": "A function which always returns true.",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {
                        "type": "string",
                        "description": "a test string",
                    },
                    "b": {
                        "type": "integer",
                        "description": "a test integer",
                    },
                },
                "required": ["a"],
            },
        },
    }


def test_assistant_definition():
    """Test the AssistantDefinition class."""

    tool: MilaTool = make_tool()
    expected = {
        "name": "test",
        "description": "a test assistant",
        "instructions": "do nothing",
        "tools": [tool],
        "model": "gpt-3.5-turbo",
        "metadata": {
            "test": "test",
        },
    }
    actual = AssistantDefinition(**expected)
    expected["tools"] = [tool.definition for tool in expected["tools"]]
    assert str(actual) == json.dumps(expected)
