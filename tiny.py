#!/usr/bin/env python3

from openai import OpenAI
import time, json

def get_horoscope(star_sign: str) -> str:
    """Get the horoscope for a given star sign."""
    print("Function called: get_horoscope")
    return f"Your horoscope for {star_sign} is: {horoscope_for(star_sign)}"

def horoscope_for(star_sign: str) -> str:
    """Get the horoscope for a given star sign."""
    return "You will be reminded of your own mortality."

LLM = OpenAI()
ASSISTANT = LLM.beta.assistants.create(
    instructions="You are a personal assistant for a busy professional named Kristen. You help them with their daily tasks.",
    name="Mila",
    model="gpt-3.5-turbo-16k",
    tools=[
        {
            "type": "function",
            "function": {
                "name": "get_horoscope",
                "description": "Get the horoscope for a given star sign.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "star_sign": {
                            "type": "string",
                            "description": "The star sign to get the horoscope for.",
                        }
                    },
                    "required": ["star_sign"]
                }
            }
        }
    ]
)
THREAD = LLM.beta.threads.create(
    messages=[
        {
            "role": "user",
            "content": "What's my horoscope for today? I was born February 2nd.",
        }
    ]
)
RUN = LLM.beta.threads.runs.create(
    thread_id=THREAD.id,
    assistant_id=ASSISTANT.id,
)
TOOL_OUTPUTS = []
while True:
    RUN = LLM.beta.threads.runs.retrieve(
        thread_id=THREAD.id,
        run_id=RUN.id,
    )
    if RUN.status == "completed":
        break
    elif RUN.status in [
        "cancelled",
        "expired",
        "failed",
    ]:
        raise RuntimeError(f"Run failed: {RUN.status}")
    elif RUN.status == "requires_action":
        for tool_call in RUN.required_action.submit_tool_outputs.tool_calls:
            arguments = json.loads(tool_call.function.arguments)
            name = tool_call.function.name
            if name == "get_horoscope":
                response = get_horoscope(**arguments)
                id = tool_call.id
                TOOL_OUTPUTS.append(
                    {
                        "tool_call_id": id,
                        "output": response,
                    }
                )
            else:
                raise RuntimeError(f"Unknown tool call: {name}")
        RUN = LLM.beta.threads.runs.submit_tool_outputs(
            thread_id=THREAD.id,
            run_id=RUN.id,
            tool_outputs=TOOL_OUTPUTS,
        )
    else:
        time.sleep(1)
MESSAGES = LLM.beta.threads.messages.list(
    thread_id=THREAD.id,
)
for message in MESSAGES.data:
    for content in message.content:
        print(content.text.value)
LLM.beta.assistants.delete(
    assistant_id=ASSISTANT.id,
)
LLM.beta.threads.delete(
    thread_id=THREAD.id,
)