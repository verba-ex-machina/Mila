"""Provide a suite of fun tools."""

import json

import requests

from mila.logging import LOGGER


def get_horoscope(star_sign: str) -> str:
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
