"""Execute the Mila framework as an all-in-one module."""

import asyncio

from . import MilaIO
from .module.discord import DiscordIO


async def main() -> None:
    """Execute the Mila framework."""
    discord = DiscordIO()
    discord.setup()
    mila = MilaIO()
    mila.setup()
    running = True
    while running:
        # Collect inputs from users to Mila.
        tasks = await discord.recv()
        for task in tasks:
            if task.content == "exit":
                running = False
            else:
                await mila.send(task)
        # Collect outputs from Mila to users.
        tasks = await mila.recv()
        for task in tasks:
            await discord.send(task)
        await asyncio.sleep(0.1)
    mila.teardown()
    discord.teardown()


if __name__ == "__main__":
    asyncio.run(main())
