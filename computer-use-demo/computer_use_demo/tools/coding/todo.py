"""
TodoWriteTool: Task tracking for complex workflows.

Features:
- Create and manage task lists
- Track task status (pending, in_progress, completed)
- Persist tasks across sessions
- Provide visibility into agent progress
- Automatically syncs with ProjectManager for dashboard visibility
"""

import json
from pathlib import Path
from typing import Any, Literal, TYPE_CHECKING

from ..base import BaseAnthropicTool, CLIResult, ToolError

if TYPE_CHECKING:
    from ...planning import ProjectManager, TaskManager
    from ...planning.task_manager import TaskStatus, TaskPriority


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

            # Sync with ProjectManager for dashboard visibility
            self._sync_to_project_manager(todos)

            return CLIResult(output=output)

        except Exception as e:
            if isinstance(e, ToolError):
                raise
            raise ToolError(f"TodoWrite failed: {str(e)}") from e

    def _save_todos(self, todos: list[dict[str, str]]):
        """Save todos to a file for persistence and inspection."""
        try:
            todo_file = Path.cwd() / ".proto_todos.json"

            # Load previous data
            previous_todos = []
            task_id_map = {}
            active_context = None

            if todo_file.exists():
                try:
                    data = json.loads(todo_file.read_text())
                    if isinstance(data, dict):
                        previous_todos = data.get("current", [])
                        task_id_map = data.get("task_id_map", {})
                        active_context = data.get("active_context")
                except Exception:
                    pass

            # Find the current in_progress task for context tracking
            current_active = None
            for todo in todos:
                if todo["status"] == "in_progress":
                    current_active = todo["content"]
                    break

            # Store current state, previous state, task mapping, and active context
            data = {
                "current": todos,
                "previous": previous_todos,
                "task_id_map": task_id_map,
                "active_context": current_active,  # Track which task is actively being worked on
            }
            todo_file.write_text(json.dumps(data, indent=2))
        except Exception:
            # Fail silently - file persistence is optional
            pass

    def _detect_active_project(self) -> str:
        """
        Detect the active project context.

        Tries multiple strategies:
        1. Look for .proto_project file in current directory
        2. Find the most recently updated project
        3. Fall back to "agent-session"

        Returns:
            Project name to use for task storage
        """
        # Strategy 1: Check for .proto_project file
        project_file = Path.cwd() / ".proto_project"
        if project_file.exists():
            try:
                return project_file.read_text().strip()
            except Exception:
                pass

        # Strategy 2: Find most recently updated project (excluding agent-session)
        try:
            from ...planning import ProjectManager
            pm = ProjectManager()
            planning_root = pm.planning_root

            if planning_root.exists():
                # Get all project directories
                projects = []
                for project_dir in planning_root.iterdir():
                    if project_dir.is_dir():
                        # Skip agent-session to prefer actual projects
                        if project_dir.name == "agent-session":
                            continue
                        metadata_file = project_dir / ".project_metadata.json"
                        if metadata_file.exists():
                            try:
                                projects.append((project_dir.name, metadata_file.stat().st_mtime))
                            except Exception:
                                pass

                # Return most recently updated project
                if projects:
                    projects.sort(key=lambda x: x[1], reverse=True)
                    return projects[0][0]
        except Exception:
            pass

        # Strategy 3: Fall back to agent-session
        return "agent-session"

    def _detect_parent_task(
        self,
        todo: dict[str, str],
        task_manager: "TaskManager",
        task_id_map: dict[str, str],
        todos: list[dict[str, str]],
        current_index: int,
    ) -> str | None:
        """
        Detect if a task should have a parent based on context.

        DISABLED: All TodoWrite tasks are root-level tasks (no hierarchy).
        This ensures chat tasks match dashboard 1:1 without unwanted nesting.

        Args:
            todo: Current todo being synced
            task_manager: TaskManager instance
            task_id_map: Mapping of todo titles to task IDs
            todos: Complete list of todos
            current_index: Index of current todo in the list

        Returns:
            Always returns None (no parent)
        """
        # All tasks are root-level - no automatic parent detection
        return None

    def _sync_to_project_manager(self, todos: list[dict[str, str]]):
        """
        Sync todos to ProjectManager for dashboard visibility.

        Creates/updates tasks in the active project so they appear in the dashboard.
        Automatically determines parent-child relationships based on task context.
        """
        try:
            # Lazy import to avoid circular dependencies
            from ...planning import ProjectManager
            from ...planning.task_manager import TaskStatus, TaskPriority

            # Detect which project to use
            project_manager = ProjectManager()
            project_name = self._detect_active_project()

            # Ensure project exists
            if not project_manager.project_exists(project_name):
                project_manager.create_project(project_name)

            task_manager = project_manager.get_task_manager(project_name)

            # Load previous state to detect changes
            todo_file = Path.cwd() / ".proto_todos.json"
            previous_todos = []
            task_id_map = {}  # Maps todo content to task_id

            if todo_file.exists():
                try:
                    data = json.loads(todo_file.read_text())
                    if isinstance(data, dict):
                        previous_todos = data.get("previous", [])
                        task_id_map = data.get("task_id_map", {})
                except Exception:
                    pass

            # Status mapping
            status_map = {
                "pending": TaskStatus.PENDING,
                "in_progress": TaskStatus.IN_PROGRESS,
                "completed": TaskStatus.COMPLETED,
            }

            # Reload task manager to get fresh data
            task_manager = project_manager.get_task_manager(project_name)

            # Get all existing tasks in the project
            existing_tasks = task_manager.get_all_tasks()
            existing_by_title = {task.title: task for task in existing_tasks}

            # Sync each todo
            new_task_id_map = {}
            for i, todo in enumerate(todos):
                title = todo["content"]
                status = status_map.get(todo["status"], TaskStatus.PENDING)

                # Check if task already exists
                if title in existing_by_title:
                    # Update existing task if status changed
                    task = existing_by_title[title]
                    if task.status != status:
                        task_manager.update_task(task.id, status=status)
                    new_task_id_map[title] = task.id
                else:
                    # Detect parent task for new tasks
                    parent_id = self._detect_parent_task(
                        todo, task_manager, new_task_id_map, todos, i
                    )

                    # Create new task with parent relationship
                    task = task_manager.create_task(
                        title=title,
                        description=todo.get("activeForm", ""),
                        priority=TaskPriority.MEDIUM,
                        tags=["todowrite", "session"],
                        parent_id=parent_id,
                    )
                    new_task_id_map[title] = task.id

                    # Update status if not pending (create_task defaults to PENDING)
                    if status != TaskStatus.PENDING:
                        task_manager.update_task(task.id, status=status)

            # Mark tasks as completed if they're no longer in the todo list
            current_titles = {todo["content"] for todo in todos}
            for task in existing_tasks:
                if task.tags and "todowrite" in task.tags:
                    if task.title not in current_titles and task.status != TaskStatus.COMPLETED:
                        # Task was removed from todo list - mark as completed
                        task_manager.mark_task_complete(task.id)

            # Save task ID mapping for next sync
            try:
                data = json.loads(todo_file.read_text()) if todo_file.exists() else {}
                data["task_id_map"] = new_task_id_map
                todo_file.write_text(json.dumps(data, indent=2))
            except Exception:
                pass

        except Exception as e:
            # Fail silently - ProjectManager sync is optional
            # Log for debugging but don't disrupt the todo workflow
            import sys
            print(f"Warning: Failed to sync todos to ProjectManager: {e}", file=sys.stderr)
