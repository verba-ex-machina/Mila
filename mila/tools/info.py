"""Provide informational tools for Mila."""

import json
import os

import aiohttp

from mila.logging import LOGGER


async def get_weather(zipcode: str) -> str:
    """Get the weather for a given location in the USA."""
    apikey = os.getenv("OPENWEATHERMAP_API_KEY")
    if not apikey:
        return json.dumps(
            {
                "error": (
                    "No OpenWeatherMap API key found. "
                    + "An API key can be obtained from "
                    + "https://openweathermap.org/."
                )
            }
        )
    base_url = "https://api.openweathermap.org/data/2.5/forecast"
    base_url += f"?zip={zipcode},us&appid={apikey}&units=imperial"
    LOGGER.info("Function called: get_weather(zipcode='%s')", zipcode)

    async with aiohttp.ClientSession() as session:
        async with session.get(base_url, timeout=5) as response:
            return await response.text()


get_weather.properties = {
    "zipcode": {
        "type": "string",
        "description": "The user's zipcode.",
    }
}
get_weather.required = ["zipcode"]
