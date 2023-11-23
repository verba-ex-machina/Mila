"""Provide a suite of fun tools."""

import json
import os

import requests

from mila.logging import LOGGER


async def get_horoscope(star_sign: str) -> str:
    """Get the horoscope for a given star sign."""
    base_url = "https://horoscope-app-api.vercel.app"
    path = "/api/v1/get-horoscope/daily"
    params = f"?sign={star_sign}&day=today"
    LOGGER.info("Function called: get_horoscope(star_sign='%s')", star_sign)
    response = requests.get(base_url + path + params, timeout=5)
    return json.dumps(response.json())


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
    response = requests.get(base_url + path, timeout=5)
    data = response.json()
    # Select only 2-box memes.
    memes = data["data"]["memes"]
    memes = [meme for meme in memes if meme["box_count"] == 2]
    data["data"]["memes"] = memes
    return json.dumps(data)


get_meme_templates.properties = {}
get_meme_templates.required = []


async def get_meme(template_id: int, text0: str, text1: str) -> str:
    """Get a meme from a template. Please make it funny."""
    # Make a POST request to the Imgflip API.
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
    response = requests.post(base_url + path, params=params, timeout=5)
    return json.dumps(response.json())


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
