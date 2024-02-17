"""Execute the Mila framework as an all-in-one module."""

import asyncio

from .module.discord import DiscordIO


async def main() -> None:
    """Execute the Mila framework."""
    discord = DiscordIO()
    discord.setup()
    running = True
    while running:
        task = await discord.recv()
        if task:
            if task.content == "exit":
                running = False
            else:
                await discord.send(task)
        await asyncio.sleep(0.1)
    discord.teardown()


if __name__ == "__main__":
    asyncio.run(main())
