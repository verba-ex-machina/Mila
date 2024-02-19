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
                tasks = await discord.recv()
                if any(task.content == "exit" for task in tasks):
                    running = False
                else:
                    await fakeio.send(tasks)
                await discord.send(await fakeio.recv())
                await asyncio.sleep(0.1)


if __name__ == "__main__":
    asyncio.run(demo())
