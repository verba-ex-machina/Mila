"""Provide a suite of utility tools."""

from mila.logging import LOGGER


async def suggest_feature(
    category: str,
    feature: str,
) -> str:
    """Suggest a feature to expand Mila's capabilities."""
    LOGGER.info("Function called: suggest_feature")
    LOGGER.info("  - Category: %s", category)
    LOGGER.info("  - Feature: %s", feature)
    return "Your feature proposal has been recorded. Thank you!"


suggest_feature.properties = {
    "category": {
        "type": "string",
        "description": "A one-word category for the feature.",
    },
    "feature": {
        "type": "string",
        "description": "The function name for the suggested feature.",
    },
}
suggest_feature.required = ["feature", "category", "implementation"]


async def submit_bug(
    tool_name: str,
    report: str,
) -> str:
    """Submit a bug report to improve Mila's performance."""
    LOGGER.info("Function called: submit_bug")
    LOGGER.info("  - Tool name: %s", tool_name)
    LOGGER.info("  - Report: %s", report)
    return "Your bug report has been recorded. Thank you!"


submit_bug.properties = {
    "tool_name": {
        "type": "string",
        "description": "The tool that caused the bug.",
    },
    "report": {
        "type": "string",
        "description": "A description of the bug.",
    },
}
submit_bug.required = ["tool_name", "report"]
