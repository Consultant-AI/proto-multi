"""
Planning Tool for Proto Multi-Agent System.

Enables agents to create and manage planning documents for complex tasks.
"""

from anthropic import Anthropic
from anthropic.types.beta import BetaMessageParam

from ...proto_logging import get_logger
from ...planning import DocumentType, PlanningDocuments, ProjectManager, TaskComplexityAnalyzer
from ..base import BaseAnthropicTool, CLIResult, ToolError, ToolResult


class PlanningTool(BaseAnthropicTool):
    """
    Tool for generating planning documents using LLM.

    This tool allows the CEO agent to create comprehensive planning documents
    for complex tasks by:
    1. Analyzing task complexity
    2. Generating appropriate planning documents
    3. Saving documents to the project folder structure
    """

    name: str = "create_planning_docs"
    api_type: str = "custom"

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key
        super().__init__()

    def to_params(self):
        """Return tool parameter schema for Anthropic API."""
        return {
            "name": self.name,
            "description": """Create comprehensive planning documents for a task or project.

Use this tool when:
- Task complexity is medium or higher
- You need structured planning before implementation
- The task involves multiple components or specialists
- You want to maintain planning documents for future reference

The tool will analyze the task, determine which planning documents to create,
and generate them using appropriate templates and prompts.

Returns paths to created planning documents.""",
            "input_schema": {
                "type": "object",
                "properties": {
                    "task": {
                        "type": "string",
                        "description": "The task or project to plan for",
                    },
                    "project_name": {
                        "type": "string",
                        "description": "Name for the project (will be used to create project folder)",
                    },
                    "context": {
                        "type": "object",
                        "description": "Optional additional context (existing project info, constraints, etc.)",
                    },
                },
                "required": ["task", "project_name"],
            },
        }

    async def __call__(
        self,
        task: str,
        project_name: str,
        context: dict | None = None,
        **kwargs,
    ) -> ToolResult | CLIResult:
        """
        Generate planning documents for a task.

        Args:
            task: The task or project to plan for
            project_name: Name for the project
            context: Optional additional context

        Returns:
            ToolResult with paths to created documents
        """
        # Validate API key early
        if not self.api_key:
            return ToolResult(error="ANTHROPIC_API_KEY is missing. Planning documents cannot be generated.")

        context = context or {}
        logger = get_logger()

        try:
            # Initialize components
            analyzer = TaskComplexityAnalyzer()
            project_manager = ProjectManager()
            client = Anthropic(api_key=self.api_key)

            # Analyze task complexity
            logger.log_event(
                event_type="planning_started",
                session_id="planning-tool",
                data={
                    "task": task,
                    "project_name": project_name,
                },
            )

            analysis = analyzer.analyze(task, context)

            logger.log_event(
                event_type="complexity_analyzed",
                session_id="planning-tool",
                data={
                    "complexity": analysis.complexity,
                    "planning_required": analysis.planning_required,
                    "estimated_steps": analysis.estimated_steps,
                    "required_specialists": analysis.required_specialists,
                    "planning_strategy": analysis.planning_strategy,
                },
            )

            if not analysis.planning_required:
                return ToolResult(
                    output=f"Task analyzed as '{analysis.complexity}' - planning documents not required.\n"
                    f"Reasoning: {analysis.reasoning}"
                )

            # Create or get project
            if project_manager.project_exists(project_name):
                project_path = project_manager.get_project_path(project_name)
                logger.log_event(
                    event_type="debug_info",
                    session_id="planning-tool",
                    data={"message": f"Using existing project at {project_path}"},
                )
            else:
                project_path = project_manager.create_project(project_name)
                logger.log_event(
                    event_type="project_created",
                    session_id="planning-tool",
                    data={"project_name": project_name, "project_path": str(project_path)},
                )

            # Generate documents based on planning strategy
            created_docs = []
            docs_to_create = []

            # Determine which docs to create based on strategy
            if analysis.planning_strategy.get("project_overview"):
                docs_to_create.append("project_overview")
            if analysis.planning_strategy.get("requirements"):
                docs_to_create.append("requirements")
            if analysis.planning_strategy.get("technical_spec"):
                docs_to_create.append("technical_spec")
            if analysis.planning_strategy.get("roadmap"):
                docs_to_create.append("roadmap")
            if analysis.planning_strategy.get("knowledge_base"):
                docs_to_create.append("knowledge_base")
            if analysis.planning_strategy.get("decisions"):
                docs_to_create.append("decisions")

            # Generate each document
            planning_context = {"task": task, "context": context, "analysis": analysis}

            for doc_type in docs_to_create:
                try:
                    content = await self._generate_document_content(
                        client, doc_type, planning_context  # type: ignore
                    )

                    doc_path = project_manager.save_document(project_name, doc_type, content)  # type: ignore

                    created_docs.append({"type": doc_type, "path": str(doc_path)})

                    logger.log_event(
                        event_type="document_generated",
                        session_id="planning-tool",
                        data={"doc_type": doc_type, "path": str(doc_path)},
                    )

                except Exception as e:
                    logger.log_error("planning-tool", e)
                    # Continue with other documents even if one fails
                    continue

            # Generate specialist plans if needed
            if analysis.planning_strategy.get("specialist_plans"):
                for specialist in analysis.required_specialists:
                    try:
                        specialist_context = planning_context.copy()
                        specialist_context["specialist"] = specialist

                        content = await self._generate_document_content(
                            client, "specialist_plan", specialist_context
                        )

                        doc_path = project_manager.save_document(
                            project_name, "specialist_plan", content, specialist=specialist
                        )

                        created_docs.append({"type": f"{specialist}_plan", "path": str(doc_path)})

                        logger.log_event(
                            event_type="document_generated",
                            session_id="planning-tool",
                            data={
                                "doc_type": "specialist_plan",
                                "specialist": specialist,
                                "path": str(doc_path),
                            },
                        )

                    except Exception as e:
                        logger.log_error("planning-tool", e)
                        continue

            logger.log_event(
                event_type="planning_completed",
                session_id="planning-tool",
                data={
                    "project_name": project_name,
                    "documents_created": len(created_docs),
                    "document_types": [doc["type"] for doc in created_docs],
                },
            )

            # Format output
            output_lines = [
                f"Planning documents created for project '{project_name}':",
                f"\nProject path: {project_path}",
                f"\nComplexity: {analysis.complexity}",
                f"Estimated steps: {analysis.estimated_steps}",
                f"Required specialists: {', '.join(analysis.required_specialists)}",
                f"\nCreated {len(created_docs)} documents:",
            ]

            for doc in created_docs:
                output_lines.append(f"  - {doc['type']}: {doc['path']}")

            return ToolResult(output="\n".join(output_lines))

        except Exception as e:
            logger.log_error("planning-tool", e)
            raise ToolError(f"Failed to create planning documents: {str(e)}")

    async def _generate_document_content(
        self, client: Anthropic, doc_type: DocumentType, context: dict
    ) -> str:
        """
        Generate document content using LLM.

        Args:
            client: Anthropic client
            doc_type: Type of document to generate
            context: Context for generation (task, analysis, etc.)

        Returns:
            Generated markdown content
        """
        # Get template
        template = PlanningDocuments.get_template(doc_type)

        # Format prompt with context
        task = context.get("task", "")
        specialist = context.get("specialist", "")

        prompt_kwargs = {
            "task": task,
            "specialist": specialist,
            "context": str(context.get("context", {})),
            "requirements": "See project overview",
            "technical_spec": "See project overview",
            "domain": specialist or "general",
        }

        # Format the generation prompt
        prompt = template.generation_prompt.format(**prompt_kwargs)

        # Call LLM to generate content
        messages: list[BetaMessageParam] = [{"role": "user", "content": prompt}]

        response = client.messages.create(
            model="claude-sonnet-4-5-20250929", max_tokens=4096, messages=messages
        )

        # Extract text from response
        content_parts = []
        for block in response.content:
            if hasattr(block, "text"):
                content_parts.append(block.text)

        return "\n".join(content_parts)
