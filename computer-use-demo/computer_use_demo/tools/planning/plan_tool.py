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

    def __init__(self, api_key: str | None = None, progress_callback=None):
        self.api_key = api_key
        self.progress_callback = progress_callback
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
            print(f"\n{'='*60}")
            print(f"PLANNING STARTED: {project_name}")
            print(f"{'='*60}\n")

            logger.log_event(
                event_type="planning_started",
                session_id="planning-tool",
                data={
                    "task": task,
                    "project_name": project_name,
                },
            )

            analysis = analyzer.analyze(task, context)
            print(f"Complexity analyzed: {analysis.complexity}")

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

            # Track progress for output
            progress_log = []
            progress_log.append(f"Starting planning for project '{project_name}'...")
            progress_log.append(f"Complexity: {analysis.complexity}")
            progress_log.append(f"Estimated steps: {analysis.estimated_steps}")
            progress_log.append(f"Required specialists: {', '.join(analysis.required_specialists)}")
            progress_log.append(f"\nCreating {len(docs_to_create)} planning documents...")

            for doc_type in docs_to_create:
                try:
                    # Print progress to terminal (visible immediately)
                    progress_msg = f"📝 Generating {doc_type} document..."
                    print(progress_msg)
                    progress_log.append(progress_msg)
                    if self.progress_callback:
                        self.progress_callback(progress_msg)

                    content = await self._generate_document_content(
                        client, doc_type, planning_context  # type: ignore
                    )

                    doc_path = project_manager.save_document(project_name, doc_type, content)  # type: ignore

                    # CRITICAL: Validate that file was actually created
                    from pathlib import Path
                    if not Path(doc_path).exists():
                        raise ToolError(f"Failed to create {doc_type} - file not found at {doc_path}")

                    created_docs.append({"type": doc_type, "path": str(doc_path)})

                    # Print completion to terminal (visible immediately)
                    completion_msg = f"✓ Created {doc_type}"
                    print(completion_msg)
                    progress_log.append(completion_msg)
                    if self.progress_callback:
                        self.progress_callback(completion_msg)

                    logger.log_event(
                        event_type="document_generated",
                        session_id="planning-tool",
                        data={"doc_type": doc_type, "path": str(doc_path)},
                    )

                except Exception as e:
                    error_msg = f"✗ Failed to generate {doc_type}: {str(e)}"
                    print(error_msg)
                    progress_log.append(error_msg)
                    if self.progress_callback:
                        self.progress_callback(error_msg)
                    logger.log_error("planning-tool", e)
                    # CRITICAL: Don't continue - fail immediately so CEO knows planning failed
                    raise ToolError(f"Planning failed while creating {doc_type}: {str(e)}")

            # NOTE: Specialist plans have been removed - all agents now collaborate on shared planning documents
            # The ROADMAP.md, TECHNICAL_SPEC.md, and other planning files are used by ALL specialists
            # Delegation happens dynamically when agents identify tasks better suited for other specialists

            # Generate task tree from roadmap
            if any(doc["type"] == "roadmap" for doc in created_docs):
                try:
                    progress_msg = "📝 Creating task tree from roadmap..."
                    print(progress_msg)
                    progress_log.append(progress_msg)
                    if self.progress_callback:
                        self.progress_callback(progress_msg)

                    tasks_path = project_manager.create_task_tree_from_roadmap(project_name)
                    if not tasks_path:
                        raise ToolError("Failed to create tasks.json - path is None")

                    # CRITICAL: Validate that tasks.json was actually created
                    from pathlib import Path
                    if not Path(tasks_path).exists():
                        raise ToolError(f"Failed to create tasks.json - file not found at {tasks_path}")

                    created_docs.append({"type": "tasks", "path": str(tasks_path)})
                    completion_msg = "✓ Created tasks.json with task tree"
                    print(completion_msg)
                    progress_log.append(completion_msg)
                    if self.progress_callback:
                        self.progress_callback(completion_msg)
                except Exception as e:
                    error_msg = f"✗ Failed to create task tree: {str(e)}"
                    print(error_msg)
                    progress_log.append(error_msg)
                    if self.progress_callback:
                        self.progress_callback(error_msg)
                    logger.log_error("planning-tool", e)
                    # CRITICAL: Fail immediately so CEO knows tasks.json creation failed
                    raise ToolError(f"Planning failed while creating tasks.json: {str(e)}")

            # Create .proto_project marker file in current directory
            # This allows other tools to detect the active project context
            try:
                from pathlib import Path
                marker_file = Path.cwd() / ".proto_project"
                marker_file.write_text(project_name)
                logger.log_event(
                    event_type="debug_info",
                    session_id="planning-tool",
                    data={"message": f"Created .proto_project marker for {project_name}"},
                )
            except Exception as e:
                # Non-critical - just log and continue
                logger.log_event(
                    event_type="debug_info",
                    session_id="planning-tool",
                    data={"message": f"Could not create .proto_project marker: {str(e)}"},
                )

            # CRITICAL: Final validation - ensure planning folder exists with all files
            from pathlib import Path
            planning_folder = Path(project_path)
            if not planning_folder.exists():
                raise ToolError(f"Planning folder does not exist at {project_path}")

            # Verify tasks.json was created (required for progress tracking)
            tasks_json_path = planning_folder / "tasks.json"
            if not tasks_json_path.exists():
                raise ToolError(f"tasks.json not found at {tasks_json_path} - cannot track progress without it")

            logger.log_event(
                event_type="planning_completed",
                session_id="planning-tool",
                data={
                    "project_name": project_name,
                    "documents_created": len(created_docs),
                    "document_types": [doc["type"] for doc in created_docs],
                },
            )

            print(f"\n{'='*60}")
            print(f"PLANNING COMPLETED: {len(created_docs)} documents created")
            print(f"{'='*60}\n")

            # Determine recommended specialist based on analysis
            recommended_specialist = "senior-developer"  # Default
            if "design" in analysis.required_specialists or "ux" in analysis.required_specialists:
                recommended_specialist = "ux-designer"
            elif "development" in analysis.required_specialists or "coding" in analysis.required_specialists:
                recommended_specialist = "senior-developer"

            # Format output with progress log
            output_lines = [
                "=" * 60,
                "PLANNING PROGRESS",
                "=" * 60,
                "",
            ]
            output_lines.extend(progress_log)
            output_lines.extend([
                "",
                "=" * 60,
                "PLANNING COMPLETE",
                "=" * 60,
                "",
                f"Project: {project_name}",
                f"Path: {project_path}",
                f"Documents created: {len(created_docs)}",
                "",
            ])

            for doc in created_docs:
                output_lines.append(f"  ✓ {doc['type']}")

            # Add NEXT STEPS guidance
            output_lines.extend([
                "",
                "=" * 60,
                "NEXT STEPS - DELEGATION REQUIRED",
                "=" * 60,
                "",
                "Planning is complete. Now you MUST delegate to the appropriate specialist:",
                "",
                f"1. Review TASKS.md at: {tasks_md_path}",
                f"2. Delegate to specialist: {recommended_specialist}",
                "",
                "Example delegation command:",
                f"  delegate_task(",
                f"    specialist=\"{recommended_specialist}\",",
                f"    task=\"Implement {project_name} per planning documents\",",
                f"    project_name=\"{project_name}\"",
                f"  )",
                "",
                "⚠️  DO NOT implement this project yourself - delegation is REQUIRED!",
                "⚠️  The specialist will use TASKS.md to track progress.",
                "",
            ])

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
