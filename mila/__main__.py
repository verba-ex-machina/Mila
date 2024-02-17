"""Execute the Mila framework as an all-in-one module."""

import asyncio

from .module.discord import DiscordIO
from .module.fake import FakeIO


async def main() -> None:
    """Execute the Mila framework."""
    with DiscordIO() as discord:
        with FakeIO() as echo:
            # For now we're running an echo server.
            running = True
            while running:
                tasks = await discord.recv()
                for task in tasks:
                    if task.content == "exit":
                        running = False
                    else:
                        await echo.send(task)
                tasks = await echo.recv()
                for task in tasks:
                    await discord.send(task)
                await asyncio.sleep(0.1)


if __name__ == "__main__":
    asyncio.run(main())
