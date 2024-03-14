"""Test the FakeAssistant class."""

import pytest

from mila.assistants.fake import FakeAssistant
from tests.common import make_assistant, make_task


@pytest.mark.asyncio
async def test_fake_assistant():
    """Test the FakeAssistant."""
    definition = make_assistant()
    assistant = FakeAssistant(definition)
    assert assistant.meta == definition
    task = make_task()
    await assistant.send([task])
    response = await assistant.recv()
    response_task = response[0]
    assert response_task.content == task.content
