"""Provide the LLM for Mila."""

import os

from langchain.chat_models import ChatOpenAI

from mila.constants import MODEL

LLM = ChatOpenAI(
    model=MODEL,
    openai_api_key=os.getenv("OPENAI_API_KEY"),
)
