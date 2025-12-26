"""
Delegation Tool for Proto Multi-Agent System.

Enables CEO agent to delegate tasks to specialist agents.
"""

from typing import TYPE_CHECKING, Any

from ...proto_logging import get_logger
from ...planning import ProjectManager
from ...planning.task_manager import TaskManager, TaskStatus
from ..base import BaseAnthropicTool, CLIResult, ToolError, ToolResult

if TYPE_CHECKING:
    from ...agents import AgentResult
    from ...agents.base_agent import BaseAgent


class DelegateTaskTool(BaseAnthropicTool):
    """
    Tool for delegating tasks to specialist agents.

    This tool allows the CEO agent to:
    1. Delegate specific work to domain specialists
    2. Pass planning context to specialists
    3. Collect and format specialist results
    """

    name: str = "delegate_task"
    api_type: str = "custom"

    def __init__(
        self,
        available_tools: list[Any] | None = None,
        api_key: str | None = None,
        delegation_depth: int = 0,
        stop_flag: Any = None,
        progress_callback: Any = None,
        delegation_status_callback: Any = None
    ):
        """
        Initialize delegation tool.

        Args:
            available_tools: Tools that can be passed to specialist agents
            api_key: Optional Anthropic API key
            delegation_depth: Current delegation depth (0 = CEO, 1 = first specialist, etc.)
                             Used for tracking and visualization, not limiting
            stop_flag: Optional callable that returns True when execution should stop
            progress_callback: Optional callable to report progress during delegation
            delegation_status_callback: Optional callable to send delegation status to UI
        """
        super().__init__()
        self.available_tools = available_tools or []
        self.api_key = api_key
        self.delegation_depth = delegation_depth
        self.stop_flag = stop_flag
        self.progress_callback = progress_callback
        self.delegation_status_callback = delegation_status_callback

    def to_params(self):
        """Return tool parameter schema for Anthropic API."""
        return {
            "name": self.name,
            "description": """Delegate a task to a specialist agent.

Use this tool when:
- The task requires domain-specific expertise
- You want to leverage specialist knowledge (marketing, development, design, etc.)
- You need focused work from an expert in a specific area
- The planning documents suggest certain specialists are needed

The specialist will receive the task, planning context, and available tools,
and will return their completed work.

Available specialists (19 total):
- Development & Technical: senior-developer, devops, qa-testing, security, technical-writer
- Product & Design: product-manager, product-strategy, ux-designer
- Data & Analytics: data-analyst, growth-analytics
- Business Functions: sales, customer-success, marketing-strategy, content-marketing
- Operations & Support: finance, legal-compliance, hr-people, business-operations, admin-coordinator

Returns the specialist's output and execution details.""",
            "input_schema": {
                "type": "object",
                "properties": {
                    "specialist": {
                        "type": "string",
                        "enum": [
                            "senior-developer", "devops", "qa-testing", "security", "technical-writer",
                            "product-manager", "product-strategy", "ux-designer",
                            "data-analyst", "growth-analytics",
                            "sales", "customer-success", "marketing-strategy", "content-marketing",
                            "finance", "legal-compliance", "hr-people", "business-operations", "admin-coordinator"
                        ],
                        "description": "Which specialist to delegate to",
                    },
                    "task": {
                        "type": "string",
                        "description": "The specific task for the specialist to complete",
                    },
                    "project_name": {
                        "type": "string",
                        "description": "Name of the project (to load planning context)",
                    },
                    "task_id": {
                        "type": "string",
                        "description": "REQUIRED: The task ID from TASKS.md that this delegation corresponds to. Get this by reading TASKS.md first.",
                    },
                    "additional_context": {
                        "type": "object",
                        "description": "Any additional context to pass to the specialist",
                    },
                },
                "required": ["specialist", "task", "project_name", "task_id"],
            },
        }

    async def __call__(
        self,
        specialist: str,
        task: str,
        project_name: str,
        task_id: str,
        additional_context: dict | None = None,
        **kwargs,
    ) -> ToolResult | CLIResult:
        """
        Delegate a task to a specialist agent.

        Args:
            specialist: Which specialist to delegate to (19 available specialists)
            task: The task to complete
            project_name: Project name for loading context
            task_id: REQUIRED task ID from TASKS.md - ensures work is tracked
            additional_context: Additional context to pass

        Returns:
            ToolResult with specialist's output
        """
        additional_context = additional_context or {}
        logger = get_logger()

        try:
            # Log delegation with depth info (no limits - delegate freely to specialists!)
            delegation_chain = "→".join(["CEO"] + ["Specialist"] * self.delegation_depth + [specialist])
            logger.log_event(
                event_type="agent_delegated",
                session_id="delegation-tool",
                data={
                    "specialist": specialist,
                    "task": task,
                    "project_name": project_name,
                    "task_id": task_id,
                    "delegation_depth": self.delegation_depth,
                    "delegation_chain": delegation_chain,
                },
            )

            # Load planning context
            project_manager = ProjectManager()
            planning_context = project_manager.get_project_context(project_name)

            # CRITICAL: Validate that TASKS.md exists and contains the task_id
            if not planning_context.get("exists"):
                raise ToolError(
                    f"Cannot delegate - project '{project_name}' has no planning context. "
                    "Create planning documents first using create_planning_docs."
                )

            # Get task manager and validate task_id exists in TASKS.md
            task_manager = project_manager.get_task_manager(project_name)
            if not task_manager:
                raise ToolError(
                    f"Cannot delegate - no task manager found for project '{project_name}'. "
                    "TASKS.md must exist before delegation."
                )

            task_obj = task_manager.get_task(task_id)
            if not task_obj:
                raise ToolError(
                    f"Cannot delegate - task_id '{task_id}' not found in TASKS.md. "
                    "Use read_planning to view TASKS.md and get a valid task_id."
                )

            # Add task_id to context so specialist knows which task they're working on
            additional_context["task_id"] = task_id
            additional_context["task_title"] = task_obj.title
            additional_context["task_status"] = task_obj.status.value

            # Combine context
            full_context = {
                **planning_context,
                **additional_context,
            }

            # Instantiate specialist agent
            specialist_agent = self._create_specialist(specialist)

            # Build enhanced task with context
            enhanced_task = self._enhance_task_with_context(task, full_context, specialist)

            # ✅ CRITICAL FIX: AUTO-UPDATE TASK STATUS TO IN_PROGRESS BEFORE EXECUTION
            # This ensures tasks are ALWAYS updated, even if specialist forgets
            logger.log_event(
                event_type="auto_task_update",
                session_id="delegation-tool",
                data={"action": "start", "task_id": task_id, "specialist": specialist},
            )

            try:
                task_manager.mark_task_in_progress(task_id)
                # Note: mark_task_in_progress() saves internally via _save_tasks()
                logger.log_event(
                    event_type="debug_info",
                    session_id="delegation-tool",
                    data={"message": f"Auto-marked task {task_id} as in_progress for {specialist}"},
                )
            except Exception as e:
                logger.log_event(
                    event_type="task_update_warning",
                    session_id="delegation-tool",
                    data={"message": f"Failed to auto-mark task in_progress: {e}"},
                )

            # Execute specialist task
            logger.log_event(
                event_type="debug_info",
                session_id="delegation-tool",
                data={"message": f"Executing task with {specialist} specialist"},
            )

            # Send delegation start status to UI
            specialist_display = specialist.replace("-", " ").title()
            if self.delegation_status_callback:
                self.delegation_status_callback(
                    f"🔄 Delegating to **{specialist_display}** for task `{task_id}`\n\n"
                    f"**Task:** {task}\n"
                    f"**Project:** {project_name}"
                )

            # Pass stop_flag and progress_callback to specialist so it can be stopped and report progress
            result = await specialist_agent.execute(
                enhanced_task,
                full_context,
                stop_flag=self.stop_flag,
                progress_callback=self.progress_callback
            )

            # Send delegation completion status to UI
            if self.delegation_status_callback:
                if result.success:
                    self.delegation_status_callback(
                        f"✅ **{specialist_display}** completed task `{task_id}`\n\n"
                        f"Iterations: {result.iterations}"
                    )
                else:
                    self.delegation_status_callback(
                        f"❌ **{specialist_display}** failed task `{task_id}`\n\n"
                        f"Error: {result.error or 'Unknown error'}"
                    )

            # Log specialist response
            logger.log_event(
                event_type="agent_response",
                session_id="ceo-agent",
                data={
                    "specialist": specialist,
                    "success": result.success,
                    "iterations": result.iterations,
                    "error": result.error,
                },
            )

            # ✅ CRITICAL FIX: AUTO-UPDATE TASK STATUS TO COMPLETED AFTER SUCCESSFUL EXECUTION
            # This ensures tasks are ALWAYS marked complete when delegation succeeds
            if result.success:
                logger.log_event(
                    event_type="auto_task_update",
                    session_id="delegation-tool",
                    data={"action": "complete", "task_id": task_id, "specialist": specialist},
                )

                try:
                    task_manager.mark_task_complete(task_id)
                    # Note: mark_task_complete() saves internally via _save_tasks()
                    logger.log_event(
                        event_type="debug_info",
                        session_id="delegation-tool",
                        data={"message": f"Auto-marked task {task_id} as completed for {specialist}"},
                    )
                except Exception as e:
                    logger.log_event(
                        event_type="task_update_warning",
                        session_id="delegation-tool",
                        data={"message": f"Failed to auto-mark task completed: {e}"},
                    )

            # Format output with delegation depth indicator for visualization
            depth_indicator = "  " * self.delegation_depth + "└─"
            delegation_level = f"[Level {self.delegation_depth + 1}]"

            # Get task info for display
            task_info = f" [{task_id}]" if task_id else ""
            specialist_display = specialist.replace("-", " ").title()

            if result.success:
                output_lines = [
                    f"\n{'='*80}",
                    f"DELEGATION COMPLETED: {specialist_display}{task_info}",
                    f"{'='*80}",
                    f"{depth_indicator} {delegation_level} Successfully delegated to {specialist_display}",
                    f"Task: {task}",
                    f"Task ID: {task_id}",
                    f"Project: {project_name}",
                    f"Iterations: {result.iterations}",
                    f"Delegation Depth: {self.delegation_depth + 1}",
                    f"\n{'-'*80}",
                    f"{specialist_display.upper()} OUTPUT:",
                    f"{'-'*80}",
                    result.output,
                    f"{'-'*80}",
                    f"END {specialist_display.upper()} OUTPUT",
                    f"{'='*80}\n",
                ]

                return ToolResult(output="\n".join(output_lines))
            else:
                error_msg = result.error or "Unknown error"
                output_lines = [
                    f"\n{'='*80}",
                    f"DELEGATION FAILED: {specialist_display}{task_info}",
                    f"{'='*80}",
                    f"{depth_indicator} {delegation_level} Failed to delegate to {specialist_display}",
                    f"Task: {task}",
                    f"Task ID: {task_id}",
                    f"Project: {project_name}",
                    f"Iterations: {result.iterations}",
                    f"Delegation Depth: {self.delegation_depth + 1}",
                    f"Error: {error_msg}",
                    f"\n{'-'*80}",
                    f"PARTIAL OUTPUT:",
                    f"{'-'*80}",
                    result.output,
                    f"{'='*80}\n",
                ]

                return ToolResult(output="\n".join(output_lines), error=error_msg)

        except Exception as e:
            logger.log_error("delegation-tool", e)
            raise ToolError(f"Failed to delegate task to {specialist}: {str(e)}")

    def _create_specialist(self, specialist: str):
        """
        Create a specialist agent instance dynamically using AGENT_REGISTRY.

        Args:
            specialist: Type of specialist (any of the 19 available specialists)

        Returns:
            Instantiated specialist agent
        """
        # Import the agent registry dynamically
        from ...agents import AGENT_REGISTRY

        if specialist not in AGENT_REGISTRY:
            available = [k for k in AGENT_REGISTRY.keys() if k != "ceo-agent"]
            raise ValueError(
                f"Unknown specialist '{specialist}'. Available specialists: {', '.join(available)}"
            )

        # Create tools with incremented delegation depth for the specialist
        # Filter out computer tool which causes API errors with specialist agents
        specialist_tools = []
        for tool in self.available_tools:
            if hasattr(tool, 'name') and tool.name == 'delegate_task':
                # Create new DelegateTaskTool with incremented depth (for tracking only)
                # Pass stop_flag, progress_callback, and delegation_status_callback so they propagate through the delegation chain
                specialist_tools.append(
                    DelegateTaskTool(
                        available_tools=self.available_tools,
                        api_key=self.api_key,
                        delegation_depth=self.delegation_depth + 1,
                        stop_flag=self.stop_flag,
                        progress_callback=self.progress_callback,
                        delegation_status_callback=self.delegation_status_callback,
                    )
                )
            elif hasattr(tool, 'api_type') and tool.api_type == 'computer_20250124':
                # Skip computer tool for specialists - they don't need it and it causes API errors
                continue
            else:
                specialist_tools.append(tool)

        agent_class = AGENT_REGISTRY[specialist]
        return agent_class(tools=specialist_tools, api_key=self.api_key)

    def _enhance_task_with_context(self, task: str, context: dict, specialist: str) -> str:
        """
        Enhance task description with planning context.

        Args:
            task: Original task
            context: Planning and project context
            specialist: Type of specialist

        Returns:
            Enhanced task description
        """
        enhanced_parts = [task]

        # CRITICAL: Add project information FIRST so specialist knows the project context
        metadata = context.get("metadata", {})
        project_name = metadata.get("project_name", "Unknown")

        if metadata:
            enhanced_parts.append("\n" + "="*60)
            enhanced_parts.append("PROJECT CONTEXT")
            enhanced_parts.append("="*60)
            enhanced_parts.append(f"\n**Project Name:** {project_name}")
            enhanced_parts.append(f"**Planning Path:** ~/Proto/{project_name}/planning/")
            enhanced_parts.append(f"**Created:** {metadata.get('created_at', 'Unknown')}")
            enhanced_parts.append("")

        # CRITICAL: Add TASK ID information - this is the task from TASKS.md you're working on
        task_id = context.get("task_id")
        if task_id:
            enhanced_parts.append("="*60)
            enhanced_parts.append("YOUR ASSIGNED TASK FROM TASKS.md")
            enhanced_parts.append("="*60)
            enhanced_parts.append(f"\n**Task ID:** {task_id}")
            enhanced_parts.append(f"**Task Title:** {context.get('task_title', 'Unknown')}")
            enhanced_parts.append(f"**Current Status:** {context.get('task_status', 'pending')}")
            enhanced_parts.append("")
            enhanced_parts.append("⚠️  **CRITICAL REQUIREMENT:**")
            enhanced_parts.append("1. Mark this task as in_progress when you start:")
            enhanced_parts.append("   ```")
            enhanced_parts.append(f'   manage_tasks(operation="start", project_name="{project_name}", task_id="{task_id}")')
            enhanced_parts.append("   ```")
            enhanced_parts.append("2. Mark this task as completed when you finish:")
            enhanced_parts.append("   ```")
            enhanced_parts.append(f'   manage_tasks(operation="complete", project_name="{project_name}", task_id="{task_id}")')
            enhanced_parts.append("   ```")
            enhanced_parts.append("")

        if metadata:
            enhanced_parts.append("**To load FULL planning context (recommended - do this first!):**")
            enhanced_parts.append("```")
            enhanced_parts.append(f'read_planning(action="get_project_context", project_name="{project_name}")')
            enhanced_parts.append("```")
            enhanced_parts.append("")
            enhanced_parts.append("This will give you access to:")
            enhanced_parts.append("- ROADMAP.md (complete project timeline)")
            enhanced_parts.append("- TECHNICAL_SPEC.md (full architecture)")
            enhanced_parts.append("- REQUIREMENTS.md (all user stories)")
            enhanced_parts.append("- TASKS.md (task tree and status)")
            enhanced_parts.append("")

        # Add shared planning documents (available to ALL specialists) - TRUNCATED versions
        documents = context.get("documents", {})

        if documents.get("project_overview"):
            enhanced_parts.append("\n## Project Overview (Truncated - call read_planning for full version)")
            enhanced_parts.append(documents["project_overview"][:500] + "...")

        if documents.get("requirements"):
            enhanced_parts.append("\n## Key Requirements (Truncated - call read_planning for full version)")
            enhanced_parts.append(documents["requirements"][:500] + "...")

        # Add ROADMAP and TECHNICAL_SPEC for all specialists to reference
        if documents.get("roadmap"):
            enhanced_parts.append("\n## Project Roadmap (Truncated - call read_planning for full version)")
            enhanced_parts.append(documents["roadmap"][:1000] + "...")

        if documents.get("technical_spec"):
            enhanced_parts.append("\n## Technical Specification (Truncated - call read_planning for full version)")
            enhanced_parts.append(documents["technical_spec"][:800] + "...")

        return "\n".join(enhanced_parts)
