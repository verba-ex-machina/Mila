"""Provide the Mila AI assistant interface."""

import hashlib
import datetime

from .logging import LOGGER, logging

class Mila:
    """Provide an interface to the Mila AI assistant backend."""

    def __init__(self):
        """Initialize Mila."""
        self._tasks = {}
    
    def _log(self, message: str) -> None:
        """Log a message."""
        LOGGER.info(message)

    def get_logger(self) -> logging.Logger:
        """Get the logger for Mila."""
        return LOGGER
    
    async def get_response(self, task_id: str) -> str:
        """Get the response to a task."""
        # TODO: Implement this.
        task = self._tasks.pop(task_id)
        response = task["response"]
        formatted_response = "\n    ".join(response.split("\n"))
        self._log(
            f"Task {task_id} completed. Response:\n    {formatted_response}"
        )
        return response

    async def new_task(self, query: str) -> str:
        """Create a new task for Mila."""
        # TODO: Implement this.
        task_id = hashlib.sha256(
            # This is a temporary stand-in for a real task ID.
            (
                query
                +str(datetime.datetime.now())
            ).encode("utf-8")
        ).hexdigest()
        self._log(f"Task received. Assigned ID {task_id}.")
        self._tasks[task_id] = {"query": query}
        return task_id
    
    async def task_complete(self, task_id: str) -> bool:
        """Check whether the task is complete."""
        # TODO: Implement this.
        self._tasks[task_id]["response"] = "This is a test response."
        return True