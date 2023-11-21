"""Provide a suite of utility tools."""

from lib.logging import LOGGER


async def get_horoscope(star_sign: str) -> str:
    """Get the horoscope for a given star sign."""
    LOGGER.info("Function called: get_horoscope")
    return f"Your horoscope for {star_sign} is: Memento mori."


get_horoscope.properties = {
    "star_sign": {
        "type": "string",
        "description": "The user's star sign.",
    }
}
get_horoscope.required = ["star_sign"]


async def suggest_feature(
    feature: str,
    category: str,
    implementation: str,
) -> str:
    """Suggest a feature to expand Mila's capabilities."""
    LOGGER.info("Function called: suggest_feature")
    LOGGER.info("- Feature: %s", feature)
    LOGGER.info("- Category: %s", category)
    LOGGER.info("- Implementation: %s", implementation)
    return f"Feature suggestion received: {feature} ({category})."


suggest_feature.properties = {
    "feature": {
        "type": "string",
        "description": "The suggested feature, in plain English.",
    },
    "category": {
        "type": "string",
        "description": "A one-word category for the feature.",
    },
    "implementation": {
        "type": "string",
        "description": "The proposed feature implementation.",
    },
}
suggest_feature.required = ["feature", "category", "implementation"]
