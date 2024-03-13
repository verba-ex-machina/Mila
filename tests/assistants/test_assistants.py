"""General tests for Assistants."""

import pytest

from mila.assistants.util import (
    assistant_dict,
    assistant_list,
    register_assistant,
)
from mila.base.collections import ASSISTANTS
from mila.base.interfaces import MilaAssistant
from mila.base.types import AssistantDefinition


@pytest.mark.asyncio
async def test_assistant_list():
    """Test the assistant_list function."""
    alist = assistant_list()
    assert len(alist) == len(ASSISTANTS)
    for assistant in ASSISTANTS.values():
        assert assistant in alist


@pytest.mark.asyncio
async def test_assistant_dict():
    """Test the assistant_dict function."""
    adict = await assistant_dict()
    assert len(adict) == len(ASSISTANTS)
    for name, assistant in ASSISTANTS.items():
        assert name in adict
        assert adict[name] == assistant.meta.description


@pytest.mark.asyncio
async def test_register_assistant():
    """Test the register_assistant function."""
    test_assistant = AssistantDefinition(
        name="TestAssistant",
        description="A test assistant.",
        instructions="Do nothing.",
        tools=[],
        model="test",
        metadata={"test": "test"},
    )
    register_assistant(test_assistant)
    assert ASSISTANTS["TestAssistant"] == MilaAssistant(test_assistant)
