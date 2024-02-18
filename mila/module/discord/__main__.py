"""Run an echo-server demo of the Discord module."""

import asyncio

from mila.module.fake import FakeIO

from . import DiscordIO


async def demo():
    """Run an echo-server demo of the Discord module."""
    running = True
    async with DiscordIO() as discord:
        async with FakeIO() as fakeio:
            while running:
                for task in await discord.recv():
                    if task.content == "exit":
                        running = False
                    else:
                        await fakeio.send(task)
                for task in await fakeio.recv():
                    await discord.send(task)
                await asyncio.sleep(0.1)


if __name__ == "__main__":
    asyncio.run(demo())
