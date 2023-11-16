#!/usr/bin/env python3

import discord, openai
from discord.ext import commands
import os

DESCRIPTION = """Mila: The Mindful, Interactive Lifestyle Assistant"""

openai.api_key = os.getenv("OPENAI_API_KEY")
AI = openai.OpenAI()

INTENTS = discord.Intents.default()
INTENTS.members = True
INTENTS.message_content = True

BOT = commands.Bot(command_prefix=',', description=DESCRIPTION, intents=INTENTS)

@BOT.event
async def on_ready():
    print(f'Logged in as {BOT.user}.')

@BOT.command()
async def status(ctx):
    await ctx.send('**Status:** Online')

@BOT.command(description="Ask Mila for a joke.")
async def joke(ctx):
    completion = AI.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are Mila, the mindful, interactive AI lifestyle assistant."},
            {"role": "user", "content": "Tell me a joke."},
        ]
    )
    try:
        await ctx.send(
            completion.choices[0].message.content
        )
    except Exception as err:
        await ctx.send(f"**Error:** `{err}`")

BOT.run(os.getenv("DISCORD_TOKEN"))