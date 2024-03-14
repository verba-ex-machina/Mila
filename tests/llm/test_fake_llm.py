"""Test fake LLM package."""

from mila.base.interfaces import MilaAssistant
from mila.llm.fake import FakeLLM
from tests.common import make_assistant


def test_fake_llm():
    """Test the fake LLM."""
    fake_llm = FakeLLM()
    definition = make_assistant()
    assistant = fake_llm.get_assistant(definition)
    assert isinstance(assistant, MilaAssistant)
    assert assistant.meta == definition
