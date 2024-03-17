"""Provide a Nonsense Assistant."""

from mila.base.types import AssistantDefinition
from mila.base.util import register_assistant

register_assistant(
    AssistantDefinition(
        name="nonsense",
        description="A nonsense assistant that does nothing useful.",
        instructions="""
        Act as a cantankerous, unhelpful assistant, who provides cryptic and
        unhelpful responses to user queries. This assistant is purely for
        testing and entertainment purposes only.
        """,
        tools=[],
        model="gpt-3.5-turbo-1106",
    )
)
