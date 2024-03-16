"""Test the Fake module."""

import pytest

from mila.assistant.fake import FakeAssistant
from mila.base.interfaces import MilaAssistant
from mila.base.types import MilaTask
from mila.io.fake import FakeIO
from mila.module.fake import FakeLLM
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


@pytest.mark.asyncio
async def test_fake_llm():
    """Test the fake LLM."""
    async with FakeLLM() as fake_llm:
        definition = make_assistant()
        assistant = await fake_llm.get_assistant(definition)
        assert isinstance(assistant, MilaAssistant)
        assert assistant.meta == definition


@pytest.mark.asyncio
async def test_fake_io():
    """Test the FakeIO class."""
    async with FakeIO() as fake_io:

        def copy_src_to_dest(task: MilaTask) -> MilaTask:
            """Copy source to destination."""
            task.dst = task.src.copy()
            return task

        # Phase 1
        assert await fake_io.recv() == []
        task = make_task()
        await fake_io.send([task])
        assert await fake_io.recv() == [copy_src_to_dest(task)]
        assert await fake_io.recv() == []
        # Phase 2
        task1 = make_task("task1")
        task2 = make_task("task2")
        await fake_io.send([task1])
        await fake_io.send([task1, task2])
        assert await fake_io.recv() == [
            copy_src_to_dest(task1),
            copy_src_to_dest(task2),
        ]
        assert await fake_io.recv() == []
