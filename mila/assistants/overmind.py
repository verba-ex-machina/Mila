"""Provide the Overmind Assistant for the Mila Framework."""

from mila.assistants.util import assistant_dict, register_assistant
from mila.base.types import MilaAssistant, MilaTool

OVERMIND_TOOLS = [
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
delegating tasks to them.
"""

register_assistant(
    MilaAssistant(
        name="Overmind",
        description="The orchestrator of the Mila Framework.",
        instructions=INSTRUCTIONS,
        tools=OVERMIND_TOOLS,
        model="gpt-3.5-turbo-1106",
    )
)
