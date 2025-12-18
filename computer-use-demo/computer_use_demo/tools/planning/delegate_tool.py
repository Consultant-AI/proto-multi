"""
Delegation Tool for Proto Multi-Agent System.

Enables CEO agent to delegate tasks to specialist agents.
"""

from typing import TYPE_CHECKING, Any

from ...logging import get_logger
from ...planning import ProjectManager
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

    def __init__(self, available_tools: list[Any] | None = None, api_key: str | None = None):
        """
        Initialize delegation tool.

        Args:
            available_tools: Tools that can be passed to specialist agents
            api_key: Optional Anthropic API key
        """
        super().__init__()
        self.available_tools = available_tools or []
        self.api_key = api_key

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

Available specialists:
- marketing-strategy: Marketing strategy, campaigns, SEO, content marketing
- senior-developer: Software engineering, architecture, full-stack development
- ux-designer: UI/UX design, visual design, interaction design

Returns the specialist's output and execution details.""",
            "input_schema": {
                "type": "object",
                "properties": {
                    "specialist": {
                        "type": "string",
                        "enum": ["marketing-strategy", "senior-developer", "ux-designer"],
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
                    "additional_context": {
                        "type": "object",
                        "description": "Any additional context to pass to the specialist",
                    },
                },
                "required": ["specialist", "task", "project_name"],
            },
        }

    async def __call__(
        self,
        specialist: str,
        task: str,
        project_name: str,
        additional_context: dict | None = None,
        **kwargs,
    ) -> ToolResult | CLIResult:
        """
        Delegate a task to a specialist agent.

        Args:
            specialist: Which specialist to delegate to (marketing-strategy, senior-developer, ux-designer)
            task: The task to complete
            project_name: Project name for loading context
            additional_context: Additional context to pass

        Returns:
            ToolResult with specialist's output
        """
        additional_context = additional_context or {}
        logger = get_logger()

        try:
            # Log delegation
            logger.log_event(
                event_type="agent_delegated",
                session_id="ceo-agent",
                data={
                    "specialist": specialist,
                    "task": task,
                    "project_name": project_name,
                },
            )

            # Load planning context
            project_manager = ProjectManager()
            planning_context = project_manager.get_project_context(project_name)

            if not planning_context.get("exists"):
                logger.log_event(
                    event_type="debug_info",
                    session_id="delegation-tool",
                    data={"message": f"No planning context found for project '{project_name}'"},
                )

            # Combine context
            full_context = {
                **planning_context,
                **additional_context,
            }

            # Instantiate specialist agent
            specialist_agent = self._create_specialist(specialist)

            # Build enhanced task with context
            enhanced_task = self._enhance_task_with_context(task, full_context, specialist)

            # Execute specialist task
            logger.log_event(
                event_type="debug_info",
                session_id="delegation-tool",
                data={"message": f"Executing task with {specialist} specialist"},
            )

            result = await specialist_agent.execute(enhanced_task, full_context)

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

            # Format output
            if result.success:
                output_lines = [
                    f"Delegation to {specialist} specialist completed successfully!",
                    f"\nTask: {task}",
                    f"Iterations: {result.iterations}",
                    f"\n--- {specialist.upper()} SPECIALIST OUTPUT ---",
                    result.output,
                    f"--- END {specialist.upper()} SPECIALIST OUTPUT ---",
                ]

                return ToolResult(output="\n".join(output_lines))
            else:
                error_msg = result.error or "Unknown error"
                output_lines = [
                    f"Delegation to {specialist} specialist failed.",
                    f"\nTask: {task}",
                    f"Iterations: {result.iterations}",
                    f"Error: {error_msg}",
                    f"\nPartial output:",
                    result.output,
                ]

                return ToolResult(output="\n".join(output_lines), error=error_msg)

        except Exception as e:
            logger.log_error("delegation-tool", e)
            raise ToolError(f"Failed to delegate task to {specialist}: {str(e)}")

    def _create_specialist(self, specialist: str):
        """
        Create a specialist agent instance.

        Args:
            specialist: Type of specialist (marketing-strategy, senior-developer, ux-designer)

        Returns:
            Instantiated specialist agent
        """
        # Lazy import to avoid circular dependencies
        from ...agents import MarketingStrategyAgent, SeniorDeveloperAgent, UXDesignerAgent

        specialist_map = {
            "marketing-strategy": MarketingStrategyAgent,
            "senior-developer": SeniorDeveloperAgent,
            "ux-designer": UXDesignerAgent,
        }

        if specialist not in specialist_map:
            raise ValueError(
                f"Unknown specialist '{specialist}'. Available: {list(specialist_map.keys())}"
            )

        agent_class = specialist_map[specialist]
        return agent_class(tools=self.available_tools, api_key=self.api_key)

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

        # Add planning documents if available
        documents = context.get("documents", {})

        if documents.get("project_overview"):
            enhanced_parts.append("\n## Project Overview")
            enhanced_parts.append(documents["project_overview"][:500] + "...")

        if documents.get("requirements"):
            enhanced_parts.append("\n## Key Requirements")
            enhanced_parts.append(documents["requirements"][:500] + "...")

        # Add specialist-specific plan if available
        specialist_plans = documents.get("specialist_plans", {})
        if specialist in specialist_plans:
            enhanced_parts.append(f"\n## Your {specialist.title()} Plan")
            enhanced_parts.append(specialist_plans[specialist][:500] + "...")

        # Add project metadata
        metadata = context.get("metadata", {})
        if metadata:
            enhanced_parts.append("\n## Project Info")
            enhanced_parts.append(f"Project: {metadata.get('project_name', 'Unknown')}")
            enhanced_parts.append(f"Created: {metadata.get('created_at', 'Unknown')}")

        return "\n".join(enhanced_parts)
