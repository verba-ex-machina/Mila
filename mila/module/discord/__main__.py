"""Run an echo-server demo of the Discord module."""

import asyncio

from . import DiscordIO


async def demo():
    """Run an echo-server demo of the Discord module."""
    running = True
    async with DiscordIO() as io:
        while running:
            tasks = await io.recv()
            for task in tasks:
                if task.content == "exit":
                    running = False
                else:
                    print(task.content)
                    await io.send(task)
            await asyncio.sleep(0.1)


if __name__ == "__main__":
    asyncio.run(demo())
