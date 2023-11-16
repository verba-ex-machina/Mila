#!/usr/bin/env python3

"""Provide a Discord bot interface for Mila."""

import os

import discord
from discord.ext import commands
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage

DESCRIPTION = """Mila: The Mindful, Interactive Lifestyle Assistant"""

LLM = ChatOpenAI(openai_api_key=os.getenv("OPENAI_API_KEY"))

INTENTS = discord.Intents.default()
INTENTS.members = True
INTENTS.message_content = True

BOT = commands.Bot(
    command_prefix=",", description=DESCRIPTION, intents=INTENTS
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
    response = LLM.invoke(
        [
            SystemMessage(
                content=f"You are {DESCRIPTION}. You are an ethical AI."
            ),
            HumanMessage(content="Tell me a joke."),
        ]
    )
    try:
        await ctx.send(response.content)
    except Exception as err:
        await ctx.send(err)


BOT.run(os.getenv("DISCORD_TOKEN"))
