"""Run an echo-server demo of the Discord module."""

import asyncio
from time import sleep

from . import DiscordIO


async def demo():
    """Run an echo-server demo of the Discord module."""
    running = True
    with DiscordIO() as io:
        while running:
            task = await io.recv()
            if task:
                if task.content == "exit":
                    running = False
                    break
                print(task.content)
                await io.send(task)
            sleep(0.1)


if __name__ == "__main__":
    asyncio.run(demo())
