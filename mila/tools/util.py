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


async def submit_bug(
    bug: str,
    category: str,
    steps: str,
    expected: str,
    actual: str,
) -> str:
    """Submit a bug report to improve Mila's performance."""
    LOGGER.info("Function called: submit_bug")
    LOGGER.info("  - Bug: %s", bug)
    LOGGER.info("  - Category: %s", category)
    LOGGER.info("  - Steps: %s", steps)
    LOGGER.info("  - Expected: %s", expected)
    LOGGER.info("  - Actual: %s", actual)
    return (
        f"Your report for `{bug}` has been recorded. "
        + "We appreciate your feedback!"
    )


submit_bug.properties = {
    "bug": {
        "type": "string",
        "description": "The function name for the reported bug.",
    },
    "category": {
        "type": "string",
        "description": "A one-word category for the bug.",
    },
    "steps": {
        "type": "string",
        "description": "The steps to reproduce the bug.",
    },
    "expected": {
        "type": "string",
        "description": "The expected behavior.",
    },
    "actual": {
        "type": "string",
        "description": "The actual behavior.",
    },
}
submit_bug.required = ["bug", "category", "steps", "expected", "actual"]
