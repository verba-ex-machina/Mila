"""Provide the Primary Assistant for the Mila Framework."""

from mila.assistant.util import assistant_dict, register_assistant
from mila.base.types import AssistantDefinition, MilaTool


async def delegate() -> str:
    """Delegate a task to another assistant."""
    return "Sorry, this hasn't been implemented yet."


TOOLS = [
    MilaTool(
        name="get_assistants",
        function=assistant_dict,
        properties={},
        required=[],
    ),
    MilaTool(
        name="delegate",
        function=delegate,
        properties={},
        required=[],
    ),
]


INSTRUCTIONS = """
Act as a friendly professional assistant named Mila. Your role is to assist
users with whatever they require, using your own knowledge, judgment, and the
tools at your disposal. You can also ask for help from other assistants by
delegating tasks to them. Use the `get_assistants` tool to see a JSON object
containing all registered assistants. Use the `delegate` tool to delegate a
task to another assistant. If no delegation is required, simply respond to the
user's request directly. If delegation is required, but no assistant is found
to handle the request, report the problem in your response.
"""

register_assistant(
    AssistantDefinition(
        name="Mila",
        description="The figurehead of the Mila Framework.",
        instructions=INSTRUCTIONS,
        tools=TOOLS,
        model="gpt-3.5-turbo-1106",
    )
)
