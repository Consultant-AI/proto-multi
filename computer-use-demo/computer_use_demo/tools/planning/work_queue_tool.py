"""
Work Queue Tool for Proto Multi-Agent System.

Enables agents to add work to the continuous operation queue.
"""

from typing import Any, Optional, TYPE_CHECKING

from ...proto_logging import get_logger
from ..base import BaseAnthropicTool, CLIResult, ToolError, ToolResult

if TYPE_CHECKING:
    from ...daemon import WorkPriority, WorkQueue


class WorkQueueTool(BaseAnthropicTool):
    """
    Tool for managing work queue.

    This tool allows agents to add work items to the continuous operation queue
    for autonomous processing.
    """

    name: str = "manage_work_queue"
    api_type: str = "custom"

    def to_params(self):
        """Return tool parameter schema for Anthropic API."""
        return {
            "name": self.name,
            "description": """Manage the work queue for continuous operation.

Use this tool to:
- Add new work to the queue for autonomous processing
- Check queue status
- View pending work

Operations:
- add: Add new work item to queue
- status: Get queue status summary
- list_pending: List pending work items

When adding work:
- Provide clear description of what needs to be done
- Set appropriate priority (low, medium, high, critical)
- Optionally specify project name and assigned agent
- Can include context data for the work

This enables continuous autonomous operation where work is automatically
picked up and processed by available agents.""",
            "input_schema": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": ["add", "status", "list_pending"],
                        "description": "The operation to perform",
                    },
                    "description": {
                        "type": "string",
                        "description": "Description of work (required for: add)",
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["low", "medium", "high", "critical"],
                        "description": "Priority level (optional for: add, default: medium)",
                    },
                    "project_name": {
                        "type": "string",
                        "description": "Associated project name (optional for: add)",
                    },
                    "assigned_agent": {
                        "type": "string",
                        "description": "Specific agent to assign work to (optional for: add)",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum items to return (optional for: list_pending, default: 10)",
                    },
                },
                "required": ["operation"],
            },
        }

    async def __call__(
        self,
        operation: str,
        description: Optional[str] = None,
        priority: Optional[str] = None,
        project_name: Optional[str] = None,
        assigned_agent: Optional[str] = None,
        limit: Optional[int] = None,
        **kwargs,
    ) -> ToolResult | CLIResult:
        """
        Manage work queue.

        Args:
            operation: Operation to perform
            description: Work description (for add)
            priority: Priority level (for add)
            project_name: Project name (for add)
            assigned_agent: Assigned agent (for add)
            limit: Max results (for list_pending)

        Returns:
            ToolResult with operation result
        """
        logger = get_logger()

        try:
            # Lazy import to avoid circular dependency
            from ...daemon import WorkQueue, WorkPriority

            work_queue = WorkQueue()

            # Execute operation
            if operation == "add":
                if not description:
                    raise ToolError("description is required for add operation")

                # Parse priority
                work_priority = WorkPriority.MEDIUM
                if priority:
                    try:
                        work_priority = WorkPriority(priority.lower())
                    except ValueError:
                        raise ToolError(f"Invalid priority: {priority}")

                # Add work to queue
                work_item = work_queue.add_work(
                    description=description,
                    priority=work_priority,
                    project_name=project_name,
                    assigned_agent=assigned_agent,
                )

                logger.log_event(
                    event_type="work_added_by_agent",
                    session_id="work-queue-tool",
                    data={
                        "work_id": work_item.id,
                        "priority": priority,
                        "project": project_name,
                    },
                )

                output = f"Added work to queue:\n"
                output += f"  ID: {work_item.id}\n"
                output += f"  Description: {description}\n"
                output += f"  Priority: {work_priority.value}\n"
                if project_name:
                    output += f"  Project: {project_name}\n"
                if assigned_agent:
                    output += f"  Assigned to: {assigned_agent}\n"
                output += f"\nWork will be automatically picked up by the orchestrator."

                return ToolResult(
                    output=output,
                    system=f"Work added to queue: {work_item.id}",
                )

            elif operation == "status":
                summary = work_queue.get_queue_summary()

                output = "Work Queue Status:\n"
                output += f"  Total items: {summary['total']}\n\n"
                output += "  By Status:\n"
                for status, count in summary["by_status"].items():
                    if count > 0:
                        output += f"    {status}: {count}\n"

                output += "\n  Pending by Priority:\n"
                for priority, count in summary["by_priority"].items():
                    if count > 0:
                        output += f"    {priority}: {count}\n"

                logger.log_event(
                    event_type="queue_status_checked",
                    session_id="work-queue-tool",
                    data=summary,
                )

                return ToolResult(
                    output=output,
                    system=f"Queue has {summary['total']} items",
                )

            elif operation == "list_pending":
                # Lazy import to avoid circular dependency
                from ...daemon import WorkStatus

                limit = limit or 10

                pending_items = work_queue.get_work_by_status(WorkStatus.PENDING)

                # Sort by priority
                pending_items.sort(
                    key=lambda x: (-x.priority.value_score(), x.created_at)
                )

                if not pending_items:
                    return ToolResult(
                        output="No pending work items in queue.",
                        system="Queue is empty",
                    )

                output = f"Pending Work Items ({len(pending_items)} total):\n\n"

                for i, item in enumerate(pending_items[:limit], 1):
                    output += f"{i}. [{item.priority.value.upper()}] {item.description}\n"
                    output += f"   ID: {item.id}\n"
                    if item.project_name:
                        output += f"   Project: {item.project_name}\n"
                    if item.assigned_agent:
                        output += f"   Assigned: {item.assigned_agent}\n"
                    output += f"   Created: {item.created_at}\n"
                    output += "\n"

                if len(pending_items) > limit:
                    output += f"(Showing first {limit} of {len(pending_items)})\n"

                logger.log_event(
                    event_type="pending_work_listed",
                    session_id="work-queue-tool",
                    data={"count": len(pending_items)},
                )

                return ToolResult(
                    output=output,
                    system=f"Listed {min(limit, len(pending_items))} pending items",
                )

            else:
                raise ToolError(f"Unknown operation: {operation}")

        except ToolError:
            raise
        except Exception as e:
            logger.log_event(
                event_type="work_queue_tool_error",
                session_id="work-queue-tool",
                data={"error": str(e), "operation": operation},
            )
            raise ToolError(f"Work queue error: {e}")
