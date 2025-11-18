"""
TodoWriteTool: Task tracking for complex workflows.

Features:
- Create and manage task lists
- Track task status (pending, in_progress, completed)
- Persist tasks across sessions
- Provide visibility into agent progress
"""

import json
from pathlib import Path
from typing import Any, Literal

from ..base import BaseAnthropicTool, CLIResult, ToolError


class TodoWriteTool(BaseAnthropicTool):
    """
    Task tracking tool for managing complex multi-step workflows.
    Use this to break down large tasks and track progress.
    """

    name: Literal["todo_write"] = "todo_write"
    api_type: Literal["custom"] = "custom"

    def to_params(self) -> Any:
        return {
            "name": self.name,
            "description": (
                "Create and manage task lists for complex workflows. Tracks task status (pending, in_progress, completed). "
                "Use this at the start of complex tasks to plan steps, and update as you progress. "
                "Provides visibility into what's done and what's remaining. "
                "IMPORTANT: Always provide both 'content' (imperative form) and 'activeForm' (present continuous) for each task."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "todos": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "content": {
                                    "type": "string",
                                    "description": (
                                        "Task description in imperative form (e.g., 'Run tests', 'Build project')"
                                    ),
                                },
                                "status": {
                                    "type": "string",
                                    "enum": ["pending", "in_progress", "completed"],
                                    "description": (
                                        "Task status. Only ONE task should be 'in_progress' at a time. "
                                        "Mark as 'completed' immediately after finishing."
                                    ),
                                },
                                "activeForm": {
                                    "type": "string",
                                    "description": (
                                        "Present continuous form shown during execution "
                                        "(e.g., 'Running tests', 'Building project')"
                                    ),
                                },
                            },
                            "required": ["content", "status", "activeForm"],
                        },
                        "description": "Complete list of tasks with their current status.",
                    },
                },
                "required": ["todos"],
            },
        }

    async def __call__(
        self,
        *,
        todos: list[dict[str, str]],
        **kwargs,
    ) -> CLIResult:
        """
        Update task list.

        Args:
            todos: List of tasks with content, status, and activeForm

        Returns:
            CLIResult with updated task list display
        """
        try:
            # Validate todos
            if not todos:
                raise ToolError("Todo list cannot be empty")

            valid_statuses = ["pending", "in_progress", "completed"]
            in_progress_count = 0

            for i, todo in enumerate(todos):
                # Validate required fields
                if "content" not in todo:
                    raise ToolError(f"Task {i+1}: missing 'content' field")
                if "status" not in todo:
                    raise ToolError(f"Task {i+1}: missing 'status' field")
                if "activeForm" not in todo:
                    raise ToolError(f"Task {i+1}: missing 'activeForm' field")

                # Validate status
                if todo["status"] not in valid_statuses:
                    raise ToolError(
                        f"Task {i+1}: invalid status '{todo['status']}'. "
                        f"Must be one of: {', '.join(valid_statuses)}"
                    )

                # Count in_progress tasks
                if todo["status"] == "in_progress":
                    in_progress_count += 1

            # Warn if multiple tasks are in progress (but don't error - allow flexibility)
            if in_progress_count > 1:
                pass  # Soft warning only

            # Format output display
            output_lines = ["📋 Task List:"]
            output_lines.append("=" * 60)

            completed_count = sum(1 for t in todos if t["status"] == "completed")
            pending_count = sum(1 for t in todos if t["status"] == "pending")
            in_progress_count = sum(1 for t in todos if t["status"] == "in_progress")

            for i, todo in enumerate(todos, 1):
                status = todo["status"]
                content = todo["content"]

                # Status icon
                if status == "completed":
                    icon = "✅"
                elif status == "in_progress":
                    icon = "🔄"
                else:  # pending
                    icon = "⏳"

                # Format line
                line = f"{i}. {icon} [{status.upper()}] {content}"
                output_lines.append(line)

            output_lines.append("=" * 60)
            output_lines.append(
                f"Progress: {completed_count} completed, "
                f"{in_progress_count} in progress, "
                f"{pending_count} pending"
            )

            output = "\n".join(output_lines)

            # Persist to file (optional - for debugging/inspection)
            self._save_todos(todos)

            return CLIResult(output=output)

        except Exception as e:
            if isinstance(e, ToolError):
                raise
            raise ToolError(f"TodoWrite failed: {str(e)}") from e

    def _save_todos(self, todos: list[dict[str, str]]):
        """Save todos to a file for persistence and inspection."""
        try:
            todo_file = Path.cwd() / ".proto_todos.json"
            todo_file.write_text(json.dumps(todos, indent=2))
        except Exception:
            # Fail silently - file persistence is optional
            pass
