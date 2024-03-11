"""Provide the Primary Assistant for the Mila Framework."""

from mila.assistants.util import assistant_dict, register_assistant
from mila.base.types import MilaAssistant, MilaTool

MILA_TOOLS = [
    MilaTool(
        name="get_assistants",
        function=assistant_dict,
        properties={},
        required=[],
    )
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
    MilaAssistant(
        name="Mila",
        description="The face of the Mila Framework.",
        instructions=INSTRUCTIONS,
        tools=MILA_TOOLS,
        model="gpt-3.5-turbo-1106",
    )
)
