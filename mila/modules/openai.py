"""Provide OpenAI LLM integration."""

import asyncio
import json
from typing import Dict, List, Union

from openai import AsyncOpenAI
from openai.types.beta.assistant import Assistant
from openai.types.beta.threads.run import RequiredActionFunctionToolCall, Run

from mila.base.interfaces import AssistantProvider, MilaAssistant, Task
from mila.base.prompts import NEW_QUERY
from mila.base.types import AssistantDefinition


class OpenAIAssistant(MilaAssistant):
    """Mila Framework OpenAI Assistant class."""

    _llm: AsyncOpenAI = None
    _assistant: Assistant = None
    _runs: List[str]
    _tasks: Dict[str, Task]
    _threads: Dict[str, str]

    def __init__(
        self, definition: AssistantDefinition, llm: AsyncOpenAI
    ) -> None:
        """Initialize the OpenAI assistant."""
        super().__init__(definition)
        self._llm = llm
        self._runs = []
        self._tasks = {}
        self._threads = {}

    async def _check_run(self, run_id: str) -> Union[None, Task]:
        """Check the status of a run."""
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

    async def _complete_run(self, run_id: str) -> Task:
        """Complete a run."""
        task = self._tasks[run_id]
        thread_id = self._threads[run_id]
        messages = await self._llm.beta.threads.messages.list(
            thread_id=thread_id
        )
        task.content = messages.data[0].content[0].text.value
        task.dst = task.src.copy()
        task.src.handler = self.meta.name
        self._runs.remove(run_id)
        return task

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

    async def _create_thread_and_run(
        self, assistant_id: str, task: Task
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

    async def _handle_task(self, task: Task) -> None:
        """Handle a single task."""
        new_run = await self._create_thread_and_run(
            assistant_id=self._assistant.id, task=task
        )
        self._runs.append(new_run.id)
        self._tasks[new_run.id] = task
        self._threads[new_run.id] = new_run.thread_id

    async def _list_assistants(self) -> List[Assistant]:
        """List all OpenAI assistants."""
        response = await self._llm.beta.assistants.list(limit=100)
        return response.data

    async def _perform_actions(self, run_id: str) -> None:
        """Perform an action on a run."""
        tool_outputs = []
        thread_id = self._threads[run_id]
        run = await self._llm.beta.threads.runs.retrieve(
            thread_id=thread_id, run_id=run_id
        )
        tool_calls = run.required_action.submit_tool_outputs.tool_calls
        tool_runs = [self._run_tool(tool_call) for tool_call in tool_calls]
        tool_outputs = await asyncio.gather(*tool_runs)
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
        tool_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)
        for tool in self.meta.tools:
            if tool.name == tool_name:
                response = await tool.function(**arguments)
                return {
                    "tool_call_id": tool_call.id,
                    "output": str(response),
                }
        raise RuntimeError(f"{self.meta.name}: Tool {tool_name} not found.")

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

    @staticmethod
    def _requires_assistant(function: callable) -> callable:
        """Require an assistant to be set."""

        async def wrapper(self: "OpenAIAssistant", *args, **kwargs):
            # pylint: disable=protected-access
            if not self._assistant:
                await self.setup()
            return await function(self, *args, **kwargs)

        return wrapper

    @_requires_assistant
    async def recv(self) -> List[Task]:
        """Receive outbound tasks from the assistant."""
        return [
            task
            for task in await asyncio.gather(
                *[self._check_run(run_id) for run_id in self._runs]
            )
            if task
        ]

    @_requires_assistant
    async def send(self, task_list: List[Task]) -> None:
        """Send tasks to the assistant."""
        coros = [self._handle_task(task) for task in task_list]
        await asyncio.gather(*coros)

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


class OpenAILLM(AssistantProvider):
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
