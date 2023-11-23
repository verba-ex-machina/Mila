"""Provide a suite of utility tools."""

from mila.logging import LOGGER


async def suggest_feature(
    feature: str,
    category: str,
    implementation: str,
) -> str:
    """Suggest a feature to expand Mila's capabilities."""
    LOGGER.info("Function called: suggest_feature")
    LOGGER.info("  - Feature: %s", feature)
    LOGGER.info("  - Category: %s", category)
    LOGGER.info("  - Implementation: %s", implementation)
    return (
        f"Your proposal for `{feature}` has been recorded. "
        + "We appreciate your suggestion!"
    )


suggest_feature.properties = {
    "feature": {
        "type": "string",
        "description": "The function name for the suggested feature.",
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
