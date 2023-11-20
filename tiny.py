#!/usr/bin/env python3

from openai import AsyncOpenAI
import time, json, asyncio

async def get_horoscope(star_sign: str) -> str:
    """Get the horoscope for a given star sign."""
    print("Function called: get_horoscope")
    return f"Your horoscope for {star_sign} is: {horoscope_for(star_sign)}"

def horoscope_for(star_sign: str) -> str:
    """Get the horoscope for a given star sign."""
    return "You are wonderful. Do something nice for yourself today. The stars demand it."

async def main():
    """Launch the Tiny Assistant demo."""
    llm = AsyncOpenAI()
    assistant = await llm.beta.assistants.create(
        instructions="You are a tiny AI assistant with a big heart.",
        name="Tiny",
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
    thread = await llm.beta.threads.create(
        messages=[
            {
                "role": "user",
                "content": "What's my horoscope for today? I'm a Capricorn.",
            }
        ]
    )
    run = await llm.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id,
    )
    tool_outputs = []
    while True:
        run = await llm.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id,
        )
        if run.status == "completed":
            break
        elif run.status in [
            "cancelled",
            "expired",
            "failed",
        ]:
            raise RuntimeError(f"Run failed: {run.status}")
        elif run.status == "requires_action":
            for tool_call in run.required_action.submit_tool_outputs.tool_calls:
                arguments = json.loads(tool_call.function.arguments)
                name = tool_call.function.name
                if name == "get_horoscope":
                    response = await get_horoscope(**arguments)
                    id = tool_call.id
                    tool_outputs.append(
                        {
                            "tool_call_id": id,
                            "output": response,
                        }
                    )
                else:
                    raise RuntimeError(f"Unknown tool call: {name}")
            run = await llm.beta.threads.runs.submit_tool_outputs(
                thread_id=thread.id,
                run_id=run.id,
                tool_outputs=tool_outputs,
            )
        else:
            time.sleep(1)
    MESSAGES = await llm.beta.threads.messages.list(
        thread_id=thread.id,
    )
    for message in MESSAGES.data:
        for content in message.content:
            print(content.text.value)
    await llm.beta.assistants.delete(
        assistant_id=assistant.id,
    )
    await llm.beta.threads.delete(
        thread_id=thread.id,
    )

if __name__ == "__main__":
    asyncio.run(main())