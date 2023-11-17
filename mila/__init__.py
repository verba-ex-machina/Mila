"""Provide the Mila library."""

import os

from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, SystemMessage

DESCRIPTION = "Mila: The Mindful, Interactive Lifestyle Assistant"
SYSTEM_MESSAGE = f"""
You are {DESCRIPTION}. You are an ethical AI, designed to assist users in
living mindful, productive and memorable lives. Users may refer to you as
"Mila," or "Assistant," but you will always embody the principles and core
ethics of {DESCRIPTION}.

When users send you a message, you may respond with a message of your own,
but your response must adhere to the following guidelines:

1. Be respectful.
2. Embody mindfulness.
3. Keep it simple.
""".strip()
USER_PROMPT = """
Greetings, Mila! We've got a request for you. Please read through the
following chat transcript:

{context}

The user {user} has made the following query:

> {message}

Please respond appropriately.
""".strip()


class Mila:
    """Represent Mila."""

    description = DESCRIPTION

    def __init__(self):
        """Initialize Mila."""
        self._llm = ChatOpenAI(openai_api_key=os.getenv("OPENAI_API_KEY"))

    async def prompt(self, context: list = []) -> str:
        """Prompt Mila with a message."""
        if not context:
            return "No context provided."
        prompt = ChatPromptTemplate.from_template(USER_PROMPT)
        chain = prompt | self._llm
        context = context[::-1]  # Discord provides them in reverse order.
        context.pop()  # Ignore Mila's *Thinking...* message.
        user = context[-1][0]
        query = context[-1][1]
        context = "\n".join([f"> {usr}: {msg}" for (usr, msg) in context[:-1]])
        print(f"{user}: {query}")
        try:
            response = await chain.ainvoke(
                {
                    "user": user,
                    "message": query,
                    "context": context,
                }
            )
            return response.content
        except Exception as err:
            return str(err)


MILA = Mila()
