"""Test fake LLM package."""

import pytest

from mila.base.interfaces import MilaAssistant
from mila.llm.fake import FakeLLM
from tests.common import make_assistant


@pytest.mark.asyncio
async def test_fake_llm():
    """Test the fake LLM."""
    async with FakeLLM() as fake_llm:
        definition = make_assistant()
        assistant = await fake_llm.get_assistant(definition)
        assert isinstance(assistant, MilaAssistant)
        assert assistant.meta == definition
