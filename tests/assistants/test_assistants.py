"""General tests for Assistants."""

import pytest

from mila.assistants.util import (
    assistant_dict,
    assistant_list,
    register_assistant,
)
from mila.base.collections import ASSISTANTS
from tests.common import make_assistant


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
        assert adict[name] == assistant.description


@pytest.mark.asyncio
async def test_register_assistant():
    """Test the register_assistant function."""
    test_assistant = make_assistant()
    register_assistant(test_assistant)
    assert ASSISTANTS[test_assistant.name] == test_assistant
