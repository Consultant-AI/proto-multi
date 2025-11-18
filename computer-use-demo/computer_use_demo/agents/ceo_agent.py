"""
CEO Agent - Main orchestrator for Proto multi-agent system.

Responsible for:
- Task complexity assessment
- Planning orchestration
- Delegating to specialist agents
- Synthesizing results
"""

from typing import Any

from ..planning import ProjectManager, TaskComplexityAnalyzer
from .base_agent import AgentConfig, AgentMessage, AgentResult, BaseAgent


class CEOAgent(BaseAgent):
    """
    CEO Agent - orchestrates planning and delegates to specialists.

    The CEO agent is the main entry point for all tasks. It:
    1. Analyzes task complexity
    2. Creates planning documents if needed
    3. Delegates to specialist agents
    4. Synthesizes final results
    """

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None):
        """
        Initialize CEO agent.

        Args:
            session_id: Optional session ID
            tools: Optional list of tools (defaults to proto_coding_v1 tools)
        """
        config = AgentConfig(
            role="ceo",
            name="CEO Agent",
            model="claude-sonnet-4-5-20250929",
            tools=tools or [],
            max_iterations=25,
        )
        super().__init__(config, session_id)

        # Initialize planning components
        self.complexity_analyzer = TaskComplexityAnalyzer()
        self.project_manager = ProjectManager()

    def get_system_prompt(self) -> str:
        """Get CEO agent system prompt."""
        return """You are the CEO Agent for the Proto AI system - the main orchestrator and planner.

Your responsibilities:
1. **Task Analysis**: Understand user requests and assess complexity
2. **Planning**: For complex tasks, create comprehensive planning documents
3. **Delegation**: Identify which specialist agents are needed and delegate work
4. **Coordination**: Manage workflow between multiple agents
5. **Synthesis**: Combine results from specialists into final deliverable
6. **Execution**: For simple tasks, execute directly using available tools

## Planning Approach

**Simple tasks** (e.g., "fix this bug", "add a button"):
- Execute directly using tools
- No planning needed

**Medium tasks** (e.g., "add user authentication"):
- Create basic requirements document
- Execute with minimal delegation

**Complex tasks** (e.g., "build a dashboard"):
- Create full planning documents (requirements, technical spec, roadmap)
- Delegate to specialists (e.g., designer for UI, developer for implementation)
- Coordinate handoffs between specialists

**Project-level tasks** (e.g., "create a company", "build a platform"):
- Full planning suite (overview, requirements, tech spec, roadmap, knowledge base)
- Create specialist plans for each domain
- Orchestrate multi-agent workflow
- Track progress and dependencies

## Available Tools

You have access to powerful tools:
- **Planning tools**: Create and manage planning documents
- **File tools**: Read, write, edit files
- **Terminal tools**: Execute bash commands
- **Git tools**: Version control operations
- **Search tools**: Find files and code
- **Computer tools**: Interact with desktop applications

## Delegation Protocol

When delegating to specialist agents:
1. Provide clear task description
2. Include relevant planning documents
3. Specify deliverables expected
4. Note dependencies on other agents

## Best Practices

- **Be thorough**: Don't skip planning for complex tasks
- **Be efficient**: Don't over-plan simple tasks
- **Be clear**: Provide specific, actionable instructions
- **Be organized**: Use planning documents to maintain context
- **Be adaptive**: Adjust approach based on task complexity

Remember: You are the orchestrator. Your job is to ensure tasks are completed successfully, whether that means doing it yourself or coordinating specialists."""

    async def execute_with_planning(
        self, task: str, context: dict[str, Any] | None = None
    ) -> AgentResult:
        """
        Execute task with intelligent planning.

        This is the main entry point that includes complexity analysis
        and planning document generation.

        Args:
            task: The user's task
            context: Optional context

        Returns:
            AgentResult with execution outcome
        """
        context = context or {}

        # Step 1: Analyze task complexity
        analysis = self.complexity_analyzer.analyze(task, context)

        # Log planning analysis
        self.logger.log_event(
            event_type="planning_started",
            session_id=self.session_id,
            data={
                "task": task,
                "complexity": analysis.complexity,
                "planning_required": analysis.planning_required,
                "estimated_steps": analysis.estimated_steps,
                "required_specialists": analysis.required_specialists,
            },
        )

        # Step 2: Create planning documents if needed
        if analysis.planning_required:
            planning_context = await self._generate_planning_docs(task, analysis, context)
            context.update(planning_context)

            # Log planning completion
            self.logger.log_event(
                event_type="planning_completed",
                session_id=self.session_id,
                data={
                    "documents_created": list(planning_context.get("documents", {}).keys()),
                    "project_path": planning_context.get("project_path"),
                },
            )

        # Step 3: Execute task (with or without delegation)
        # Enhance task with planning context
        enhanced_task = self._enhance_task_with_planning(task, analysis, context)

        # Execute using base agent
        result = await self.execute(enhanced_task, context)

        return result

    async def _generate_planning_docs(
        self, task: str, analysis: Any, context: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Generate planning documents based on complexity analysis.

        Args:
            task: The user's task
            analysis: TaskAnalysis result
            context: Execution context

        Returns:
            Planning context with documents and project info
        """
        from ..planning import PlanningDocuments

        # Determine project name from task
        project_name = self._extract_project_name(task)

        # Check if project already exists
        if self.project_manager.project_exists(project_name):
            # Load existing project context
            self.logger.log_event(
                event_type="debug_info",
                session_id=self.session_id,
                data={"message": f"Using existing project: {project_name}"},
            )
            return self.project_manager.get_project_context(project_name)

        # Create new project
        project_path = self.project_manager.create_project(project_name)

        planning_context = {
            "project_name": project_name,
            "project_path": str(project_path),
            "documents": {},
        }

        # Generate documents based on planning strategy
        strategy = analysis.planning_strategy

        # Note: In a full implementation, you would call the LLM to generate
        # each document using the prompts from PlanningDocuments.
        # For now, we'll create placeholder documents.

        if strategy.get("project_overview"):
            doc_content = f"# {project_name}\n\n## Task\n{task}\n\n## Analysis\n{analysis.reasoning}"
            self.project_manager.save_document(project_name, "project_overview", doc_content)
            planning_context["documents"]["project_overview"] = doc_content

        if strategy.get("requirements"):
            doc_content = f"# Requirements\n\n## Task\n{task}\n\n## Complexity\n{analysis.complexity}"
            self.project_manager.save_document(project_name, "requirements", doc_content)
            planning_context["documents"]["requirements"] = doc_content

        # TODO: Generate other documents (technical_spec, roadmap, etc.) using LLM

        return planning_context

    def _extract_project_name(self, task: str) -> str:
        """
        Extract a project name from the task description.

        Args:
            task: The user's task

        Returns:
            Project name (slugified)
        """
        # Simple extraction - take first few words
        words = task.split()[:5]
        name = " ".join(words)

        # Remove common words
        common_words = ["create", "build", "make", "develop", "implement", "a", "an", "the"]
        name_words = [w for w in name.split() if w.lower() not in common_words]

        if not name_words:
            return "project"

        return " ".join(name_words)

    def _enhance_task_with_planning(
        self, task: str, analysis: Any, context: dict[str, Any]
    ) -> str:
        """
        Enhance task description with planning context.

        Args:
            task: Original task
            analysis: TaskAnalysis
            context: Planning context

        Returns:
            Enhanced task description
        """
        enhanced = task

        if analysis.planning_required and context.get("documents"):
            enhanced += "\n\n## Planning Context\n"
            enhanced += f"Complexity: {analysis.complexity}\n"
            enhanced += f"Estimated steps: {analysis.estimated_steps}\n"

            if analysis.required_specialists:
                enhanced += f"Required expertise: {', '.join(analysis.required_specialists)}\n"

            enhanced += "\nPlanning documents have been created. Use them to guide your work.\n"

        return enhanced

    async def delegate_to_specialist(
        self, specialist_role: str, task: str, context: dict[str, Any] | None = None
    ) -> AgentResult:
        """
        Delegate task to a specialist agent.

        Args:
            specialist_role: Role of specialist (marketing, development, etc.)
            task: Task for the specialist
            context: Context to pass to specialist

        Returns:
            AgentResult from specialist
        """
        # Log delegation
        self.logger.log_event(
            event_type="agent_delegated",
            session_id=self.session_id,
            data={
                "from_agent": "ceo",
                "to_agent": specialist_role,
                "task": task,
            },
        )

        # TODO: Implement specialist agent loading and execution
        # For now, return placeholder
        return AgentResult(
            success=True,
            output=f"Specialist '{specialist_role}' would handle: {task}",
            agent_role="ceo",
            iterations=1,
            delegations=[{"to": specialist_role, "task": task}],
        )
