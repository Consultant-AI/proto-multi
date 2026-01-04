"""
Project Management Tool for Proto Multi-Agent System.

Enables agents to list, select, and manage projects.
"""

from typing import Any, Optional

from ...proto_logging import get_logger
from ...planning.project_manager import ProjectManager
from ..base import BaseAnthropicTool, CLIResult, ToolError, ToolResult


class ProjectTool(BaseAnthropicTool):
    """
    Tool for managing projects (list, select, get context).

    This tool allows agents to discover existing projects and decide
    whether to continue work on an existing project or create a new one.
    """

    name: str = "manage_projects"
    api_type: str = "custom"

    def to_params(self):
        """Return tool parameter schema for Anthropic API."""
        return {
            "name": self.name,
            "description": """Manage and discover projects (dual-structure architecture).

Use this tool to:
- List all existing projects from projects/
- Get details about a specific project
- Check if a project exists
- Get project context (tasks, knowledge, planning docs from .proto/planning/)

This helps you decide whether to:
1. Continue work on an existing project
2. Create a new project for a new conversation/task

Operations:
- list: List all projects (sorted by most recent, shows both dual-structure and legacy)
- get: Get details about a specific project by name
- exists: Check if a project exists
- context: Get full project context (planning docs, tasks, knowledge from .proto/planning/)

All projects follow dual-structure:
- Planning/meta in projects/{project}/.proto/planning/
- Actual code in projects/{project}/

Returns project information to help with decision making.""",
            "input_schema": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": ["list", "get", "exists", "context"],
                        "description": "The operation to perform",
                    },
                    "project_name": {
                        "type": "string",
                        "description": "Project name (required for: get, exists, context)",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of projects to return (optional for: list, default: 10)",
                    },
                },
                "required": ["operation"],
            },
        }

    async def __call__(
        self,
        operation: str,
        project_name: Optional[str] = None,
        limit: Optional[int] = None,
        **kwargs,
    ) -> ToolResult | CLIResult:
        """
        Manage projects.

        Args:
            operation: Operation to perform
            project_name: Name of project (for operations that need it)
            limit: Max number of results (for list)

        Returns:
            ToolResult with project information
        """
        logger = get_logger()

        try:
            project_manager = ProjectManager()

            # Execute operation
            if operation == "list":
                projects = project_manager.list_projects()
                limit = limit or 10

                if not projects:
                    return ToolResult(
                        output="No projects found. You can create a new project using the create_planning_docs tool.",
                        system="No existing projects",
                    )

                # Format project list
                project_list = []
                for i, project in enumerate(projects[:limit]):
                    project_list.append(
                        f"{i+1}. {project['project_name']} (slug: {project['slug']})\n"
                        f"   Created: {project.get('created_at', 'unknown')}\n"
                        f"   Updated: {project.get('updated_at', 'unknown')}\n"
                        f"   Status: {project.get('status', 'active')}"
                    )

                output = f"Found {len(projects)} project(s):\n\n" + "\n\n".join(project_list)
                if len(projects) > limit:
                    output += f"\n\n(Showing first {limit} of {len(projects)})"

                logger.log_event(
                    event_type="projects_listed",
                    session_id="project-tool",
                    data={"count": len(projects)},
                )

                return ToolResult(
                    output=output,
                    system=f"Listed {min(limit, len(projects))} of {len(projects)} projects",
                )

            elif operation == "get":
                if not project_name:
                    raise ToolError("project_name is required for get operation")

                if not project_manager.project_exists(project_name):
                    return ToolResult(
                        output=f"Project '{project_name}' does not exist.",
                        system=f"Project not found: {project_name}",
                    )

                project_path = project_manager.get_project_path(project_name)
                metadata = project_manager._load_metadata(project_path)

                # Get basic statistics
                task_manager = project_manager.get_task_manager(project_name)
                knowledge_store = project_manager.get_knowledge_store(project_name)

                task_summary = task_manager.get_task_summary() if task_manager else {}
                knowledge_summary = knowledge_store.get_knowledge_summary() if knowledge_store else {}

                details = [
                    f"Project: {metadata.get('project_name', project_name)}",
                    f"Slug: {metadata.get('slug', 'unknown')}",
                    f"Status: {metadata.get('status', 'active')}",
                    f"Created: {metadata.get('created_at', 'unknown')}",
                    f"Last Updated: {metadata.get('updated_at', 'unknown')}",
                    f"",
                    f"Tasks:",
                    f"  Total: {task_summary.get('total', 0)}",
                    f"  Pending: {task_summary.get('pending', 0)}",
                    f"  In Progress: {task_summary.get('in_progress', 0)}",
                    f"  Completed: {task_summary.get('completed', 0)}",
                    f"",
                    f"Knowledge:",
                    f"  Total Entries: {knowledge_summary.get('total', 0)}",
                ]

                return ToolResult(
                    output="\n".join(details),
                    system=f"Retrieved project details for {project_name}",
                )

            elif operation == "exists":
                if not project_name:
                    raise ToolError("project_name is required for exists operation")

                exists = project_manager.project_exists(project_name)

                if exists:
                    project_path = project_manager.get_project_path(project_name)
                    metadata = project_manager._load_metadata(project_path)
                    return ToolResult(
                        output=f"Yes, project '{project_name}' exists.\n"
                        f"Last updated: {metadata.get('updated_at', 'unknown')}",
                        system=f"Project exists: {project_name}",
                    )
                else:
                    return ToolResult(
                        output=f"No, project '{project_name}' does not exist.\n"
                        f"You can create it using the create_planning_docs tool.",
                        system=f"Project does not exist: {project_name}",
                    )

            elif operation == "context":
                if not project_name:
                    raise ToolError("project_name is required for context operation")

                context = project_manager.get_project_context(project_name)

                if not context.get("exists"):
                    return ToolResult(
                        output=f"Project '{project_name}' does not exist.",
                        system=f"Project not found: {project_name}",
                    )

                # Format context summary
                output_lines = [
                    f"Project Context: {context['metadata']['project_name']}",
                    f"",
                    f"Planning Documents:",
                ]

                for doc_type in context.get("documents", {}).keys():
                    if doc_type != "specialist_plans":
                        output_lines.append(f"  ✓ {doc_type}")

                if "specialist_plans" in context.get("documents", {}):
                    plans = context["documents"]["specialist_plans"]
                    output_lines.append(f"  ✓ specialist_plans ({len(plans)} agents)")

                output_lines.extend([
                    f"",
                    f"Tasks Summary:",
                    f"  Total: {context['tasks'].get('total', 0)}",
                    f"  Pending: {context['tasks'].get('pending', 0)}",
                    f"  In Progress: {context['tasks'].get('in_progress', 0)}",
                    f"  Completed: {context['tasks'].get('completed', 0)}",
                ])

                if context['tasks'].get('pending_tasks'):
                    output_lines.append(f"\n  Top Pending Tasks:")
                    for task in context['tasks']['pending_tasks']:
                        output_lines.append(f"    - {task['title']} [{task['priority']}]")

                if context['tasks'].get('in_progress_tasks'):
                    output_lines.append(f"\n  In Progress:")
                    for task in context['tasks']['in_progress_tasks']:
                        assigned = f" (assigned to {task['assigned_agent']})" if task.get('assigned_agent') else ""
                        output_lines.append(f"    - {task['title']}{assigned}")

                output_lines.extend([
                    f"",
                    f"Knowledge Summary:",
                    f"  Total Entries: {context['knowledge'].get('total', 0)}",
                ])

                if context['knowledge'].get('recent_entries'):
                    output_lines.append(f"\n  Recent Knowledge:")
                    for entry in context['knowledge']['recent_entries']:
                        output_lines.append(f"    - {entry['title']} [{entry['type']}]")

                logger.log_event(
                    event_type="project_context_loaded",
                    session_id="project-tool",
                    data={"project": project_name},
                )

                return ToolResult(
                    output="\n".join(output_lines),
                    system=f"Loaded context for {project_name}",
                )

            else:
                raise ToolError(f"Unknown operation: {operation}")

        except ToolError:
            raise
        except Exception as e:
            logger.log_event(
                event_type="project_error",
                session_id="project-tool",
                data={"error": str(e), "operation": operation},
            )
            raise ToolError(f"Project management error: {e}")
