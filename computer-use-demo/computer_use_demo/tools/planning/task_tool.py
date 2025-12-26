"""
Task Management Tool for Proto Multi-Agent System.

Enables agents to create, update, and query tasks within projects.
"""

from pathlib import Path
from typing import Any, Optional

from ...proto_logging import get_logger
from ...planning.project_manager import ProjectManager
from ...planning.task_manager import TaskManager, TaskPriority, TaskStatus
from ..base import BaseAnthropicTool, CLIResult, ToolError, ToolResult


class TaskTool(BaseAnthropicTool):
    """
    Tool for managing project tasks.

    This tool allows agents to create, update, query, and track tasks
    throughout project execution.
    """

    name: str = "manage_tasks"
    api_type: str = "custom"

    def to_params(self):
        """Return tool parameter schema for Anthropic API."""
        return {
            "name": self.name,
            "description": """Manage tasks for the current project.

Use this tool to:
- Create new tasks for work that needs to be done
- Update task status (pending, in_progress, completed, blocked)
- Query tasks by status, agent, or tag
- Add notes to tasks
- Track dependencies between tasks
- Get task summaries and statistics

Operations:
- create: Create a new task
- update: Update an existing task
- complete: Mark a task as completed
- block: Mark a task as blocked
- start: Mark a task as in progress
- list: List tasks (optionally filtered)
- get: Get a specific task by ID
- summary: Get task statistics
- add_note: Add a note to a task
- add_dependency: Add a dependency between tasks
- start_spec: Start specification phase for a task
- update_spec: Update specification details
- complete_spec: Complete specification phase
- start_implementation: Begin implementation phase
- add_commit: Track a git commit for a task
- add_test_result: Track test results for a task

Returns task information or list of tasks based on operation.""",
            "input_schema": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": [
                            "create",
                            "update",
                            "complete",
                            "block",
                            "start",
                            "list",
                            "get",
                            "summary",
                            "add_note",
                            "add_dependency",
                            "start_spec",
                            "update_spec",
                            "complete_spec",
                            "start_implementation",
                            "add_commit",
                            "add_test_result",
                        ],
                        "description": "The operation to perform",
                    },
                    "project_name": {
                        "type": "string",
                        "description": "Name of the project (required for all operations)",
                    },
                    "task_id": {
                        "type": "string",
                        "description": "Task ID (required for: update, complete, block, start, get, add_note, add_dependency)",
                    },
                    "title": {
                        "type": "string",
                        "description": "Task title (required for: create)",
                    },
                    "description": {
                        "type": "string",
                        "description": "Task description (optional for: create, update)",
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["low", "medium", "high", "critical"],
                        "description": "Task priority (optional for: create, update)",
                    },
                    "assigned_agent": {
                        "type": "string",
                        "description": "Agent to assign task to (optional for: create, update)",
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Task tags (optional for: create, update)",
                    },
                    "filter_status": {
                        "type": "string",
                        "enum": ["pending", "in_progress", "completed", "blocked", "cancelled"],
                        "description": "Filter by status (optional for: list)",
                    },
                    "filter_agent": {
                        "type": "string",
                        "description": "Filter by assigned agent (optional for: list)",
                    },
                    "filter_tag": {
                        "type": "string",
                        "description": "Filter by tag (optional for: list)",
                    },
                    "note": {
                        "type": "string",
                        "description": "Note text (required for: add_note, block)",
                    },
                    "depends_on_task_id": {
                        "type": "string",
                        "description": "Task ID that this task depends on (required for: add_dependency)",
                    },
                    "spec_context": {
                        "type": "string",
                        "description": "Specification context/overview (optional for: update_spec)",
                    },
                    "acceptance_criteria": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of acceptance criteria (optional for: update_spec)",
                    },
                    "implementation_checklist": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Implementation checklist items (optional for: update_spec)",
                    },
                    "spec_notes": {
                        "type": "string",
                        "description": "Specification notes (optional for: update_spec)",
                    },
                    "commit_hash": {
                        "type": "string",
                        "description": "Git commit hash (required for: add_commit)",
                    },
                    "commit_message": {
                        "type": "string",
                        "description": "Git commit message (required for: add_commit)",
                    },
                    "test_name": {
                        "type": "string",
                        "description": "Test name (required for: add_test_result)",
                    },
                    "test_passed": {
                        "type": "boolean",
                        "description": "Whether test passed (required for: add_test_result)",
                    },
                    "test_details": {
                        "type": "string",
                        "description": "Test result details (optional for: add_test_result)",
                    },
                },
                "required": ["operation", "project_name"],
            },
        }

    async def __call__(
        self,
        operation: str,
        project_name: str,
        task_id: Optional[str] = None,
        title: Optional[str] = None,
        description: Optional[str] = None,
        priority: Optional[str] = None,
        assigned_agent: Optional[str] = None,
        tags: Optional[list[str]] = None,
        filter_status: Optional[str] = None,
        filter_agent: Optional[str] = None,
        filter_tag: Optional[str] = None,
        note: Optional[str] = None,
        depends_on_task_id: Optional[str] = None,
        spec_context: Optional[str] = None,
        acceptance_criteria: Optional[list[str]] = None,
        implementation_checklist: Optional[list[str]] = None,
        spec_notes: Optional[str] = None,
        commit_hash: Optional[str] = None,
        commit_message: Optional[str] = None,
        test_name: Optional[str] = None,
        test_passed: Optional[bool] = None,
        test_details: Optional[str] = None,
        **kwargs,
    ) -> ToolResult | CLIResult:
        """
        Manage project tasks.

        Args:
            operation: Operation to perform
            project_name: Name of the project
            task_id: Task ID (for operations that need it)
            title: Task title (for create)
            description: Task description
            priority: Task priority
            assigned_agent: Agent to assign to
            tags: Task tags
            filter_status: Status filter (for list)
            filter_agent: Agent filter (for list)
            filter_tag: Tag filter (for list)
            note: Note text (for add_note, block)
            depends_on_task_id: Dependency task ID (for add_dependency)
            spec_context: Specification context (for update_spec)
            acceptance_criteria: Acceptance criteria list (for update_spec)
            implementation_checklist: Implementation checklist (for update_spec)
            spec_notes: Specification notes (for update_spec)
            commit_hash: Git commit hash (for add_commit)
            commit_message: Git commit message (for add_commit)
            test_name: Test name (for add_test_result)
            test_passed: Test pass/fail status (for add_test_result)
            test_details: Test result details (for add_test_result)

        Returns:
            ToolResult with task information
        """
        logger = get_logger()

        try:
            # Get project path
            project_manager = ProjectManager()
            project_slug = project_manager.slugify_project_name(project_name)
            project_path = project_manager.planning_root / project_slug

            if not project_path.exists() and operation != "create":
                raise ToolError(
                    f"Project '{project_name}' not found. Create planning docs first."
                )

            # Initialize task manager
            task_manager = TaskManager(project_path)

            # Execute operation
            if operation == "create":
                if not title:
                    raise ToolError("title is required for create operation")

                # Ensure project exists
                project_path.mkdir(parents=True, exist_ok=True)

                task = task_manager.create_task(
                    title=title,
                    description=description or "",
                    priority=TaskPriority(priority) if priority else TaskPriority.MEDIUM,
                    assigned_agent=assigned_agent,
                    tags=tags,
                )

                logger.log_event(
                    event_type="task_created",
                    session_id="task-tool",
                    data={"task_id": task.id, "title": task.title, "project": project_name},
                )

                return ToolResult(
                    output=f"Created task '{task.title}' (ID: {task.id})",
                    system=f"Task created successfully:\n"
                    f"  ID: {task.id}\n"
                    f"  Title: {task.title}\n"
                    f"  Priority: {task.priority.value}\n"
                    f"  Status: {task.status.value}",
                )

            elif operation == "update":
                if not task_id:
                    raise ToolError("task_id is required for update operation")

                task = task_manager.update_task(
                    task_id=task_id,
                    title=title,
                    description=description,
                    priority=TaskPriority(priority) if priority else None,
                    assigned_agent=assigned_agent,
                    add_tags=tags,
                )

                if not task:
                    raise ToolError(f"Task {task_id} not found")

                return ToolResult(
                    output=f"Updated task '{task.title}'",
                    system=f"Task {task_id} updated successfully",
                )

            elif operation == "complete":
                if not task_id:
                    raise ToolError("task_id is required for complete operation")

                task = task_manager.mark_task_complete(task_id)
                if not task:
                    raise ToolError(f"Task {task_id} not found")

                logger.log_event(
                    event_type="task_completed",
                    session_id="task-tool",
                    data={"task_id": task.id, "title": task.title, "project": project_name},
                )

                return ToolResult(
                    output=f"Marked task '{task.title}' as completed",
                    system=f"Task {task_id} completed at {task.completed_at}",
                )

            elif operation == "start":
                if not task_id:
                    raise ToolError("task_id is required for start operation")

                task = task_manager.mark_task_in_progress(task_id)
                if not task:
                    raise ToolError(f"Task {task_id} not found")

                return ToolResult(
                    output=f"Marked task '{task.title}' as in progress",
                    system=f"Task {task_id} is now in progress",
                )

            elif operation == "block":
                if not task_id:
                    raise ToolError("task_id is required for block operation")

                task = task_manager.mark_task_blocked(task_id, reason=note)
                if not task:
                    raise ToolError(f"Task {task_id} not found")

                return ToolResult(
                    output=f"Marked task '{task.title}' as blocked",
                    system=f"Task {task_id} is now blocked" + (f": {note}" if note else ""),
                )

            elif operation == "list":
                # Apply filters
                if filter_status:
                    tasks = task_manager.get_tasks_by_status(TaskStatus(filter_status))
                elif filter_agent:
                    tasks = task_manager.get_tasks_by_agent(filter_agent)
                elif filter_tag:
                    tasks = task_manager.get_tasks_by_tag(filter_tag)
                else:
                    tasks = task_manager.get_all_tasks()

                if not tasks:
                    return ToolResult(
                        output="No tasks found matching the criteria",
                        system="Task list is empty",
                    )

                # Format task list
                task_list = []
                for task in tasks:
                    task_list.append(
                        f"- [{task.status.value}] {task.title} (ID: {task.id[:8]}, Priority: {task.priority.value})"
                        + (f" - Assigned to: {task.assigned_agent}" if task.assigned_agent else "")
                    )

                return ToolResult(
                    output=f"Found {len(tasks)} task(s):\n" + "\n".join(task_list),
                    system=f"Listed {len(tasks)} tasks",
                )

            elif operation == "get":
                if not task_id:
                    raise ToolError("task_id is required for get operation")

                task = task_manager.get_task(task_id)
                if not task:
                    raise ToolError(f"Task {task_id} not found")

                details = [
                    f"Task: {task.title}",
                    f"ID: {task.id}",
                    f"Status: {task.status.value}",
                    f"Priority: {task.priority.value}",
                    f"Description: {task.description}" if task.description else "",
                    f"Assigned to: {task.assigned_agent}" if task.assigned_agent else "",
                    f"Tags: {', '.join(task.tags)}" if task.tags else "",
                    f"Dependencies: {len(task.dependencies)} task(s)" if task.dependencies else "",
                    f"Created: {task.created_at}",
                    f"Updated: {task.updated_at}",
                    f"Notes: {len(task.notes)}" if task.notes else "",
                ]

                return ToolResult(
                    output="\n".join([d for d in details if d]),
                    system=f"Retrieved task {task_id}",
                )

            elif operation == "summary":
                summary = task_manager.get_task_summary()

                output = [
                    f"Task Summary for '{project_name}':",
                    f"  Total: {summary['total']}",
                    f"  Pending: {summary['pending']}",
                    f"  In Progress: {summary['in_progress']}",
                    f"  Completed: {summary['completed']}",
                    f"  Blocked: {summary['blocked']}",
                    f"",
                    f"By Priority:",
                    f"  Critical: {summary['by_priority']['critical']}",
                    f"  High: {summary['by_priority']['high']}",
                    f"  Medium: {summary['by_priority']['medium']}",
                    f"  Low: {summary['by_priority']['low']}",
                ]

                return ToolResult(
                    output="\n".join(output),
                    system=f"Task summary generated for {project_name}",
                )

            elif operation == "add_note":
                if not task_id or not note:
                    raise ToolError("task_id and note are required for add_note operation")

                task = task_manager.add_task_note(task_id, note)
                if not task:
                    raise ToolError(f"Task {task_id} not found")

                return ToolResult(
                    output=f"Added note to task '{task.title}'",
                    system=f"Note added to task {task_id}",
                )

            elif operation == "add_dependency":
                if not task_id or not depends_on_task_id:
                    raise ToolError(
                        "task_id and depends_on_task_id are required for add_dependency operation"
                    )

                success = task_manager.add_dependency(task_id, depends_on_task_id)
                if not success:
                    raise ToolError(f"Could not add dependency (task not found)")

                task = task_manager.get_task(task_id)
                return ToolResult(
                    output=f"Added dependency to task '{task.title}'",
                    system=f"Task {task_id} now depends on {depends_on_task_id}",
                )

            elif operation == "start_spec":
                if not task_id:
                    raise ToolError("task_id is required for start_spec operation")

                task = task_manager.get_task(task_id)
                if not task:
                    raise ToolError(f"Task {task_id} not found")

                task.start_specification()
                task_manager.save_tasks()

                return ToolResult(
                    output=f"Started specification phase for task '{task.title}'",
                    system=f"Task {task_id} specification is now in progress",
                )

            elif operation == "update_spec":
                if not task_id:
                    raise ToolError("task_id is required for update_spec operation")

                task = task_manager.get_task(task_id)
                if not task:
                    raise ToolError(f"Task {task_id} not found")

                task.update_specification(
                    context=spec_context,
                    acceptance_criteria=acceptance_criteria,
                    checklist=implementation_checklist,
                    notes=spec_notes,
                )
                task_manager.save_tasks()

                return ToolResult(
                    output=f"Updated specification for task '{task.title}'",
                    system=f"Task {task_id} specification updated",
                )

            elif operation == "complete_spec":
                if not task_id:
                    raise ToolError("task_id is required for complete_spec operation")

                task = task_manager.get_task(task_id)
                if not task:
                    raise ToolError(f"Task {task_id} not found")

                task.complete_specification()
                task_manager.save_tasks()

                return ToolResult(
                    output=f"Completed specification for task '{task.title}'",
                    system=f"Task {task_id} specification is now complete. Ready for implementation.",
                )

            elif operation == "start_implementation":
                if not task_id:
                    raise ToolError("task_id is required for start_implementation operation")

                task = task_manager.get_task(task_id)
                if not task:
                    raise ToolError(f"Task {task_id} not found")

                # Verify spec is complete before starting implementation
                spec_status = task.get_spec_status()
                if spec_status != "completed":
                    raise ToolError(
                        f"Cannot start implementation for task {task_id}: "
                        f"specification must be completed first (current status: {spec_status})"
                    )

                task.start_implementation()
                task_manager.save_tasks()

                return ToolResult(
                    output=f"Started implementation for task '{task.title}'",
                    system=f"Task {task_id} implementation phase has begun",
                )

            elif operation == "add_commit":
                if not task_id or not commit_hash or not commit_message:
                    raise ToolError(
                        "task_id, commit_hash, and commit_message are required for add_commit operation"
                    )

                task = task_manager.get_task(task_id)
                if not task:
                    raise ToolError(f"Task {task_id} not found")

                task.add_commit(commit_hash, commit_message)
                task_manager.save_tasks()

                return ToolResult(
                    output=f"Tracked commit {commit_hash[:8]} for task '{task.title}'",
                    system=f"Commit {commit_hash} added to task {task_id}",
                )

            elif operation == "add_test_result":
                if not task_id or not test_name or test_passed is None:
                    raise ToolError(
                        "task_id, test_name, and test_passed are required for add_test_result operation"
                    )

                task = task_manager.get_task(task_id)
                if not task:
                    raise ToolError(f"Task {task_id} not found")

                task.add_test_result(test_name, test_passed, test_details or "")
                task_manager.save_tasks()

                result_text = "passed" if test_passed else "failed"
                return ToolResult(
                    output=f"Recorded test result for task '{task.title}': {test_name} {result_text}",
                    system=f"Test result added to task {task_id}",
                )

            else:
                raise ToolError(f"Unknown operation: {operation}")

        except ToolError:
            raise
        except Exception as e:
            logger.log_event(
                event_type="task_error",
                session_id="task-tool",
                data={"error": str(e), "operation": operation},
            )
            raise ToolError(f"Task management error: {e}")
