"""Test fake LLM package."""

from mila.base.interfaces import MilaAssistant
from mila.base.types import AssistantDefinition
from mila.llm.fake import FakeLLM


def test_fake_llm():
    """Test the fake LLM."""
    fake_llm = FakeLLM()
    definition = AssistantDefinition(
        name="test assistant",
        description="test assistant description",
        instructions="test assistant instructions",
        tools=[],
        model="gpt-3.5-turbo",
        metadata={},
    )
    assistant = fake_llm.get_assistant(definition)
    assert isinstance(assistant, MilaAssistant)
    assert assistant.meta == definition
