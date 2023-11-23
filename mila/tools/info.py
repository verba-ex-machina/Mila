"""Provide informational tools for Mila."""

import json
import os

import aiohttp
import serpapi
from bs4 import BeautifulSoup

from mila.logging import LOGGER


async def get_weather(zipcode: str) -> str:
    """Get the weather for a given location in the USA."""
    api_key = os.getenv("OPENWEATHERMAP_API_KEY")
    if not api_key:
        err = (
            "No OpenWeatherMap API key found. An API key can be obtained from"
            " https://openweathermap.org/."
        )
        LOGGER.error(err)
        return json.dumps(
            {
                "error": err,
            }
        )
    base_url = "https://api.openweathermap.org/data/2.5/forecast"
    base_url += f"?zip={zipcode},us&appid={api_key}&units=imperial"
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


async def scrape_url(url: str) -> str:
    """Scrape a given URL for its content. Scrapes raw HTML."""
    LOGGER.info("Function called: scrape_url(url='%s')", url)
    async with aiohttp.ClientSession() as session:
        async with session.get(url, timeout=5) as response:
            content = await response.text()
            soup = BeautifulSoup(content, "html.parser")
            return soup.get_text()


scrape_url.properties = {
    "url": {
        "type": "string",
        "description": "The URL to scrape.",
    }
}
scrape_url.required = ["url"]


async def search_duckduckgo(query: str) -> str:
    """Retrieve the top-10 DuckDuckGo results for a given query."""
    api_key = os.getenv("SERPAPI_API_KEY")
    if not api_key:
        err = (
            "No SerpAPI API key found. An API key can be obtained from"
            " https://serpapi.com/."
        )
        LOGGER.error(err)
        return json.dumps(
            {
                "error": err,
            }
        )
    LOGGER.info("Function called: search_duckduckgo(query='%s')", query)
    client = serpapi.GoogleSearch(
        {
            "engine": "duckduckgo",
            "q": query,
            "kl": "us-en",
            "api_key": api_key,
        }
    )
    results = client.get_dict()
    top_results = results["organic_results"][:10]  # top 10 results
    formatted_results = [
        # Compress to essentials.
        {
            "title": result["title"],
            "link": result["link"],
            "snippet": result["snippet"],
        }
        for result in top_results
    ]
    return json.dumps(formatted_results)


search_duckduckgo.properties = {
    "query": {
        "type": "string",
        "description": "The query to search for.",
    }
}
search_duckduckgo.required = ["query"]
