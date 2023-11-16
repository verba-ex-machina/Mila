#!/usr/bin/env python3

"""Launch Mila as a service."""

import os

import discord
from discord.ext import commands

from lib import Mila
from lib.constants import DESCRIPTION
MILA = Mila()

INTENTS = discord.Intents.default()
INTENTS.members = True
INTENTS.message_content = True

BOT = commands.Bot(
    command_prefix=";", description=DESCRIPTION, intents=INTENTS
)


@BOT.event
async def on_ready():
    """Print a message when the bot is ready."""
    print(f"Logged in as {BOT.user}.")


@BOT.command()
async def status(ctx):
    """Print the bot's status."""
    await ctx.send("**Status:** Online")


@BOT.command(description="Ask Mila for a joke.")
async def joke(ctx):
    """Ask Mila for a joke."""
    await ctx.send(MILA._consciousness.prompt("Tell me a joke."))


BOT.run(os.getenv("DISCORD_TOKEN"))
