"""Provide OpenAI LLM integration."""

import asyncio
import json
from dataclasses import dataclass, field
from typing import Dict, List, Union

from openai import AsyncOpenAI
from openai.types.beta.assistant import Assistant
from openai.types.beta.threads.run import RequiredActionFunctionToolCall, Run

from mila.base.interfaces import MilaAssistant, MilaLLM, MilaTask
from mila.base.prompts import NEW_QUERY
from mila.base.types import AssistantDefinition


@dataclass
class OpenAIAssistant(MilaAssistant):
    """Mila Framework OpenAI Assistant class."""

    _llm: AsyncOpenAI = None
    _assistant: Assistant = None
    _runs: List[str] = field(default_factory=list)
    _tasks: Dict[str, MilaTask] = field(default_factory=dict)
    _threads: Dict[str, str] = field(default_factory=dict)

    def __init__(
        self, definition: AssistantDefinition, llm: AsyncOpenAI
    ) -> None:
        """Initialize the OpenAI assistant."""
        print(f"Initializing OpenAI assistant {definition.name}.")
        super().__init__(definition)
        self._llm = llm
        self._runs = []
        self._tasks = {}
        self._threads = {}

    @staticmethod
    def _requires_assistant(function: callable) -> callable:
        """Require an assistant to be set."""

        async def wrapper(self: "OpenAIAssistant", *args, **kwargs):
            # pylint: disable=protected-access
            if not self._assistant:
                await self.setup()
            return await function(self, *args, **kwargs)

        return wrapper

    async def _create(self, definition: AssistantDefinition) -> Assistant:
        """Create a new OpenAI assistant."""
        return await self._llm.beta.assistants.create(
            name=definition.name,
            description=definition.description,
            instructions=definition.instructions,
            tools=[tool.definition for tool in definition.tools],
            model=definition.model,
            metadata={
                "hash": hash(definition),
                **definition.metadata,
            },
        )

    async def _list_assistants(self) -> List[Assistant]:
        """List all OpenAI assistants."""
        response = await self._llm.beta.assistants.list(limit=100)
        return response.data

    async def _update(
        self, assistant_id: str, definition: AssistantDefinition
    ) -> None:
        """Update the specified OpenAI assistant."""
        return await self._llm.beta.assistants.update(
            assistant_id=assistant_id,
            name=definition.name,
            description=definition.description,
            instructions=definition.instructions,
            tools=[tool.definition for tool in definition.tools],
            model=definition.model,
            metadata={
                "hash": hash(definition),
                **definition.metadata,
            },
        )

    async def setup(self) -> None:
        """Set up the assistant."""
        for assistant in await self._list_assistants():
            if assistant.name == self.meta.name:
                if (
                    "hash" not in assistant.metadata.keys()
                    or assistant.metadata["hash"] != hash(self.meta)
                ):
                    self._assistant = await self._update(
                        assistant.id, self.meta
                    )
                    return
                self._assistant = assistant
        self._assistant = await self._create(self.meta)

    async def _perform_actions(self, run_id: str) -> None:
        """Perform an action on a run."""
        tool_outputs = []
        thread_id = self._threads[run_id]
        print(
            f"{self.meta.name}: Performing actions for run {run_id} in",
            f"thread {thread_id}.",
        )
        run = await self._llm.beta.threads.runs.retrieve(
            thread_id=thread_id, run_id=run_id
        )
        tool_calls = run.required_action.submit_tool_outputs.tool_calls
        tool_runs = [self._run_tool(tool_call) for tool_call in tool_calls]
        tool_outputs = [
            output for output in await asyncio.gather(*tool_runs) if output
        ]
        if tool_outputs:
            await self._llm.beta.threads.runs.submit_tool_outputs(
                thread_id=thread_id,
                run_id=run_id,
                tool_outputs=tool_outputs,
            )

    async def _run_tool(
        self, tool_call: RequiredActionFunctionToolCall
    ) -> dict:
        """Run a tool."""
        print(
            f"{self.meta.name}: Running tool {tool_call.function.name}.\n"
            f"  - Call: {tool_call}"
        )
        tool_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)
        output = {}
        for tool in self.meta.tools:
            if tool.name == tool_name:
                response = await tool.function(**arguments)
                output = {
                    "tool_call_id": tool_call.id,
                    "output": str(response),
                }
        if not output:
            print(f"{self.meta.name}: Tool {tool_name} not found.")
        return output

    async def _check_run(self, run_id: str) -> Union[None, MilaTask]:
        """Check the status of a run."""
        print(f"{self.meta.name}: Checking run {run_id}.")
        run = await self._llm.beta.threads.runs.retrieve(
            thread_id=self._threads[run_id], run_id=run_id
        )
        if not run.status == "completed":
            if run.status in ["cancelled", "expired", "failed"]:
                raise RuntimeError(
                    f"{self.meta.name}: Run failed. ({run.status})"
                )
            if run.status == "requires_action":
                await self._perform_actions(run_id)
            return None
        return await self._complete_run(run_id)

    async def _complete_run(self, run_id: str) -> MilaTask:
        """Complete a run."""
        self._runs.remove(run_id)
        task = self._tasks[run_id]
        thread_id = self._threads[run_id]
        messages = await self._llm.beta.threads.messages.list(
            thread_id=thread_id
        )
        task.content = messages.data[0].content[0].text.value
        task.dst = task.src.copy()
        task.src.handler = self.meta.name
        return task

    @_requires_assistant
    async def recv(self) -> List[MilaTask]:
        """Receive outbound tasks from the assistant."""
        outbound_tasks = []
        if self._runs:
            print(
                f"{self.meta.name}: Retrieving outbound tasks. ({self._runs})"
            )
            coros = [self._check_run(run_id) for run_id in self._runs]
            task_list = await asyncio.gather(*coros)
            outbound_tasks = [task for task in task_list if task]
        return outbound_tasks

    async def _create_thread_and_run(
        self, assistant_id: str, task: MilaTask
    ) -> Run:
        """Create a new OpenAI run and thread."""
        run = await self._llm.beta.threads.create_and_run(
            assistant_id=assistant_id,
            thread={
                "messages": [
                    {
                        "role": "user",
                        "content": NEW_QUERY.format(
                            context=task.context, query=task.content
                        ),
                    }
                ],
            },
        )
        return run

    async def _handle_task(self, task: MilaTask) -> None:
        """Handle a single task."""
        print(f"{self.meta.name}: Handling task {task}.")
        new_run = await self._create_thread_and_run(
            assistant_id=self._assistant.id, task=task
        )
        self._runs.append(new_run.id)
        self._tasks[new_run.id] = task
        self._threads[new_run.id] = new_run.thread_id
        print(f"{self.meta.name}: Task assigned to run {new_run.id}.")

    @_requires_assistant
    async def send(self, task_list: List[MilaTask]) -> None:
        """Send tasks to the assistant."""
        if task_list:
            print(f"{self.meta.name}: Received {len(task_list)} tasks.")
            coros = [self._handle_task(task) for task in task_list]
            await asyncio.gather(*coros)


class OpenAILLM(MilaLLM):
    """Mila Framework OpenAI LLM class."""

    _llm: AsyncOpenAI = None
    _assistants: Dict[str, OpenAIAssistant] = {}

    def __init__(self) -> None:
        """Initialize the OpenAI LLM."""
        self._llm = AsyncOpenAI()

    async def get_assistant(
        self, definition: AssistantDefinition
    ) -> MilaAssistant:
        """Return an assistant for the given definition."""
        if definition.name not in self._assistants.keys():
            self._assistants[definition.name] = OpenAIAssistant(
                definition=definition, llm=self._llm
            )
        return self._assistants[definition.name]

    async def _assistant_delete(self, assistant_id: str) -> None:
        """Delete the specified OpenAI assistant."""
        await self._llm.beta.assistants.delete(assistant_id)

    async def _assistant_list(self) -> List[Assistant]:
        """List all OpenAI assistants."""
        response = await self._llm.beta.assistants.list(limit=100)
        return response.data

    async def teardown(self) -> None:
        """Perform OpenAI LLM teardown."""
        for assistant in await self._assistant_list():
            # Don't delete assistants that aren't part of Mila.
            # All of ours use the "hash" metadata key.
            # This isn't a perfect solution, but it'll do for now.
            if "hash" in assistant.metadata.keys():
                await self._assistant_delete(assistant.id)
