"""Mila Framework task database module."""

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from mila.base.interfaces import TaskDB


class SqliteDB(TaskDB):
    """SQLite database handler class."""

    engine: AsyncEngine

    async def setup(self) -> None:
        """Initialize the storage channel."""
        self.engine = create_async_engine(
            "sqlite+aiosqlite:///:memory:", echo=True
        )

    async def teardown(self) -> None:
        """Close the storage channel."""
        await self.engine.dispose()
