"""Provide a suite of fun tools."""

import os
import random

import aiohttp

from ..logging import LOGGER


async def get_horoscope(star_sign: str) -> str:
    """Get the horoscope for a given star sign."""
    base_url = "https://horoscope-app-api.vercel.app"
    path = "/api/v1/get-horoscope/daily"
    params = f"?sign={star_sign}&day=today"
    LOGGER.info("Function called: get_horoscope(star_sign='%s')", star_sign)

    async with aiohttp.ClientSession() as session:
        async with session.get(
            base_url + path + params, timeout=5
        ) as response:
            return await response.text()


get_horoscope.properties = {
    "star_sign": {
        "type": "string",
        "description": "The user's star sign. Lowercase.",
    }
}
get_horoscope.required = ["star_sign"]


async def get_meme_templates() -> str:
    """Get available meme templates."""
    base_url = "https://api.imgflip.com"
    path = "/get_memes"
    LOGGER.info("Function called: get_meme_templates()")

    async with aiohttp.ClientSession() as session:
        async with session.get(base_url + path, timeout=5) as response:
            data = await response.json()
            # There are far too many meme templates; this saves tokens.
            memes = random.sample(
                [
                    meme
                    for meme in data["data"]["memes"]
                    if meme["box_count"] == 2
                ],
                5,
            )
            return (
                "Here are five possible templates, "
                f"selected randomly:\n\n{memes}"
            )


get_meme_templates.properties = {}
get_meme_templates.required = []


async def get_meme(template_id: int, text0: str, text1: str) -> str:
    """Get a meme from a template. Please make it funny."""
    username = os.getenv("IMGFLIP_USERNAME")
    password = os.getenv("IMGFLIP_PASSWORD")
    base_url = "https://api.imgflip.com"
    path = "/caption_image"
    params = {
        "template_id": template_id,
        "username": username,
        "password": password,
        "text0": text0,
        "text1": text1,
    }
    LOGGER.info(
        "Function called: get_meme(template_id=%s, text0='%s', text1='%s')",
        template_id,
        text0,
        text1,
    )

    async with aiohttp.ClientSession() as session:
        async with session.post(
            base_url + path, data=params, timeout=5
        ) as response:
            meme = await response.json()
            response = f"Here's your meme: {meme['data']['url']}"
    return response


get_meme.properties = {
    "template_id": {
        "type": "integer",
        "description": "The ID of the meme template.",
    },
    "text0": {
        "type": "string",
        "description": "The text for the first part of the meme.",
    },
    "text1": {
        "type": "string",
        "description": "The text for the second part of the meme.",
    },
}
get_meme.required = ["template_id", "text0", "text1"]
