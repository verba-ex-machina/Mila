"""Test Mila interfaces."""

import pytest

from mila.base.interfaces import ContextManager


class DemoCM(ContextManager):
    """Define a test ContextManager class."""

    set_up: bool = False
    torn_down: bool = False

    async def setup(self) -> None:
        """Set up the test LLM."""
        self.set_up = True

    async def teardown(self) -> None:
        """Tear down the test LLM."""
        self.torn_down = True


@pytest.mark.asyncio
async def test_llm():
    """Test the ContextManager abstract base class."""
    async with DemoCM() as ctx_mgr:
        assert ctx_mgr.set_up
        assert not ctx_mgr.torn_down
    assert ctx_mgr.torn_down
