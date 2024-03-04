"""Provide access to the OpenAI Runs feature."""

import json

from .llm import LLM
from .logging import LOGGER
from .tools import TOOLS


class Run:
    """Provide an abstraction for the OpenAI Runs API."""

    def __init__(
        self,
        thread_id: str,
        assistant_id: str,
    ):
        """Initialize the Run."""
        self._thread_id = thread_id
        self._assistant_id = assistant_id
        self._run = None

    async def _spawn_run(self):
        """Spawn a new run."""
        self._run = await LLM.beta.threads.runs.create(
            thread_id=self._thread_id,
            assistant_id=self._assistant_id,
        )

    async def _update(self):
        """Update the run."""
        if not self._run:
            await self._spawn_run()
        else:
            self._run = await LLM.beta.threads.runs.retrieve(
                thread_id=self._thread_id,
                run_id=self._run.id,
            )

    async def check(self) -> bool:
        """Check whether a query run is complete."""
        await self._update()
        complete = False
        if self._run.status == "completed":
            LOGGER.info("Run completed.")
            complete = True
        elif self._run.status in [
            "cancelled",
            "expired",
            "failed",
        ]:
            LOGGER.error("Run failed: %s", self._run.status)
            complete = True
        elif self._run.status == "requires_action":
            tool_outputs = []
            LOGGER.info("Run requires action.")
            for (
                tool_call
            ) in self._run.required_action.submit_tool_outputs.tool_calls:
                arguments = json.loads(tool_call.function.arguments)
                name = tool_call.function.name
                found = False
                for tool in TOOLS.definitions:
                    if tool["function"]["name"] == name:
                        found = True
                        function = TOOLS.get(name)
                        if function:
                            response = await function(
                                **arguments,
                            )
                            tool_call_id = tool_call.id
                            tool_outputs.append(
                                {
                                    "tool_call_id": tool_call_id,
                                    "output": response,
                                }
                            )
                        else:
                            LOGGER.error(
                                "Undefined function: %s",
                                name,
                            )
                            complete = True
                if not found:
                    LOGGER.error("Undefined tool: %s", name)
                    complete = True
            if tool_outputs:
                LOGGER.info("Submitting tool outputs.")
                self._run = await LLM.beta.threads.runs.submit_tool_outputs(
                    thread_id=self._thread_id,
                    run_id=self._run.id,
                    tool_outputs=tool_outputs,
                )
        return complete

    async def id(self) -> str:
        """Get the ID of the run."""
        await self._update()
        return self._run.id

    async def response(self) -> str:
        """Get the response of the run."""
        await self._update()
        return_value = ""
        if self._run.status in ["cancelled", "expired", "failed"]:
            LOGGER.error("Run failed: %s", self._run.status)
            return_value = f"Run error: {self._run.status}"
        elif self._run.status == "requires_action":
            LOGGER.error("Error in LLM function call.")
            return_value = "Error in LLM function call."
        else:
            messages = await LLM.beta.threads.messages.list(
                thread_id=self._thread_id,
            )
            return_value = messages.data[0].content[0].text.value
        return return_value
