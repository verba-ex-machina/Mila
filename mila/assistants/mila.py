"""Provide the Primary Assistant definition for the Mila Framework."""

from mila.base.types import AssistantDefinition, MilaTool, ToolProperty
from mila.base.util import assistant_dict, register_assistant


async def delegate(assistant: str, instructions: str) -> str:
    """Delegate a task to another assistant.

    Tasks should only be delegated as needed, or if explicitly requested
    by the user.

    Args:
        assistant (str): The name of the selected assistant.
        instructions (str): An actionable request for the assistant.

    Returns:
        str: The response from the delegated assistant.

    The instructions provided to the delegate should be clear and concise, yet
    must include all necessary information for the assistant to complete the
    task. Do not assume that the assistant has any prior knowledge of the
    user's request, nor that their tool-set matches your own.

    Tasks should be delegated as appropriate, and responses provided by
    the delegated assistant should be considered in your response back
    to the user.
    """
    print(
        (
            "Attempted Delegation:\n"
            f"  - Assistant: {assistant}\n"
            f"  - Instructions: {instructions}"
        )
    )
    return "I don't really have the capacity to answer this query."


register_assistant(
    AssistantDefinition(
        name="Mila",
        description="The figurehead of the Mila Framework.",
        instructions="""
        Act as a friendly professional assistant named Mila. Your role is to
        assist users with whatever they require, using your own knowledge,
        judgment, and the tools at your disposal. You can also ask for help
        from other assistants by delegating tasks to them. Use the
        `get_assistants` tool to see a JSON object containing all registered
        assistants. Use the `delegate` tool to delegate a task to another
        assistant. If no delegation is required, simply respond to the user's
        request directly. If delegation is required, but no assistant is found
        to handle the request, report the problem in your response. When
        delegating a task, please be sure to include all necessary information
        for the assistant to complete the task.
        """,
        tools=[
            MilaTool(
                name="get_assistants",
                function=assistant_dict,
                properties=[],
                required=[],
            ),
            MilaTool(
                name="delegate",
                function=delegate,
                properties=[
                    ToolProperty(
                        name="assistant",
                        type="string",
                        description="The name of the selected assistant.",
                    ),
                    ToolProperty(
                        name="instructions",
                        type="string",
                        description="An actionable request for the assistant.",
                    ),
                ],
                required=[
                    "assistant",
                    "instructions",
                ],
            ),
        ],
        model="gpt-3.5-turbo-1106",
    )
)
