"""
Read Planning Tool for Proto Multi-Agent System.

Enables agents to read and access planning documents and project context.
"""

from ...logging import get_logger
from ...planning import DocumentType, ProjectManager
from ..base import BaseAnthropicTool, CLIResult, ToolError, ToolResult


class ReadPlanningTool(BaseAnthropicTool):
    """
    Tool for reading planning documents and project context.

    This tool allows agents to:
    1. List available projects
    2. Read specific planning documents
    3. Get comprehensive project context
    4. Check if planning exists for a task
    """

    name: str = "read_planning"
    api_type: str = "custom"

    def to_params(self):
        """Return tool parameter schema for Anthropic API."""
        return {
            "name": self.name,
            "description": """Read planning documents and project context.

Use this tool when:
- You need to check if planning documents exist for a project
- You want to read specific planning documents (overview, requirements, etc.)
- You need comprehensive project context before starting work
- You want to see what projects have been planned

The tool can list all projects, read specific documents, or provide complete project context.

Available document types:
- project_overview: High-level project information
- requirements: Detailed requirements and user stories
- technical_spec: Technical architecture and design
- roadmap: Project timeline and milestones
- knowledge_base: Domain knowledge and best practices
- decisions: Decision log
- specialist_plan: Specialist-specific plans (requires specialist name)

Returns the requested planning information.""",
            "input_schema": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["list_projects", "read_document", "get_project_context", "check_exists"],
                        "description": "What planning operation to perform",
                    },
                    "project_name": {
                        "type": "string",
                        "description": "Name of the project (required for read_document, get_project_context, check_exists)",
                    },
                    "document_type": {
                        "type": "string",
                        "enum": [
                            "project_overview",
                            "requirements",
                            "technical_spec",
                            "roadmap",
                            "knowledge_base",
                            "decisions",
                            "specialist_plan",
                        ],
                        "description": "Type of document to read (required for read_document action)",
                    },
                    "specialist": {
                        "type": "string",
                        "description": "Specialist name (required when document_type is specialist_plan)",
                    },
                },
                "required": ["action"],
            },
        }

    async def __call__(
        self,
        action: str,
        project_name: str | None = None,
        document_type: str | None = None,
        specialist: str | None = None,
        **kwargs,
    ) -> ToolResult | CLIResult:
        """
        Read planning documents or project context.

        Args:
            action: What to do (list_projects, read_document, get_project_context, check_exists)
            project_name: Name of the project
            document_type: Type of document to read
            specialist: Specialist name (for specialist_plan documents)

        Returns:
            ToolResult with requested planning information
        """
        logger = get_logger()
        project_manager = ProjectManager()

        try:
            if action == "list_projects":
                return await self._list_projects(project_manager)

            elif action == "check_exists":
                if not project_name:
                    raise ToolError("project_name is required for check_exists action")
                return await self._check_exists(project_manager, project_name)

            elif action == "read_document":
                if not project_name or not document_type:
                    raise ToolError("project_name and document_type are required for read_document action")
                return await self._read_document(project_manager, project_name, document_type, specialist)  # type: ignore

            elif action == "get_project_context":
                if not project_name:
                    raise ToolError("project_name is required for get_project_context action")
                return await self._get_project_context(project_manager, project_name)

            else:
                raise ToolError(f"Unknown action: {action}")

        except Exception as e:
            logger.log_error("read-planning-tool", e)
            raise ToolError(f"Failed to read planning information: {str(e)}")

    async def _list_projects(self, project_manager: ProjectManager) -> ToolResult:
        """List all available projects."""
        projects = project_manager.list_projects()

        if not projects:
            return ToolResult(output="No planning projects found.")

        output_lines = [f"Found {len(projects)} planning projects:\n"]

        for project in projects:
            output_lines.append(f"- {project['project_name']}")
            output_lines.append(f"  Slug: {project['slug']}")
            output_lines.append(f"  Status: {project.get('status', 'unknown')}")
            output_lines.append(f"  Created: {project.get('created_at', 'unknown')}")
            output_lines.append(f"  Updated: {project.get('updated_at', 'unknown')}")
            output_lines.append("")

        return ToolResult(output="\n".join(output_lines))

    async def _check_exists(self, project_manager: ProjectManager, project_name: str) -> ToolResult:
        """Check if a project exists."""
        exists = project_manager.project_exists(project_name)

        if exists:
            project_path = project_manager.get_project_path(project_name)
            return ToolResult(
                output=f"Project '{project_name}' exists.\nPath: {project_path}"
            )
        else:
            return ToolResult(
                output=f"Project '{project_name}' does not exist.\n"
                "You can create it using the create_planning_docs tool."
            )

    async def _read_document(
        self,
        project_manager: ProjectManager,
        project_name: str,
        document_type: DocumentType,
        specialist: str | None,
    ) -> ToolResult:
        """Read a specific planning document."""
        # Check if project exists
        if not project_manager.project_exists(project_name):
            raise ToolError(f"Project '{project_name}' does not exist")

        # Load document
        content = project_manager.load_document(project_name, document_type, specialist=specialist)

        if content is None:
            return ToolResult(
                output=f"Document '{document_type}' not found in project '{project_name}'.\n"
                "It may not have been created yet."
            )

        # Format output
        doc_title = document_type.replace("_", " ").title()
        if specialist:
            doc_title = f"{specialist.title()} {doc_title}"

        output_lines = [
            f"=== {doc_title} ===",
            f"Project: {project_name}",
            "",
            content,
        ]

        return ToolResult(output="\n".join(output_lines))

    async def _get_project_context(self, project_manager: ProjectManager, project_name: str) -> ToolResult:
        """Get comprehensive project context."""
        context = project_manager.get_project_context(project_name)

        if not context.get("exists"):
            return ToolResult(
                output=f"Project '{project_name}' does not exist.\n"
                "You can create it using the create_planning_docs tool."
            )

        # Format output
        output_lines = [
            f"=== Project Context: {project_name} ===",
            "",
            "## Metadata",
            f"Path: {context['path']}",
        ]

        metadata = context.get("metadata", {})
        if metadata:
            output_lines.append(f"Status: {metadata.get('status', 'unknown')}")
            output_lines.append(f"Created: {metadata.get('created_at', 'unknown')}")
            output_lines.append(f"Updated: {metadata.get('updated_at', 'unknown')}")

        # List available documents
        documents = context.get("documents", {})
        if documents:
            output_lines.append("\n## Available Documents")
            for doc_type in documents:
                if doc_type == "specialist_plans":
                    specialist_plans = documents[doc_type]
                    output_lines.append(f"- Specialist Plans:")
                    for specialist in specialist_plans:
                        output_lines.append(f"  - {specialist}")
                else:
                    output_lines.append(f"- {doc_type}")

        # Add summary of each document (first 200 chars)
        if documents:
            output_lines.append("\n## Document Summaries")
            for doc_type, content in documents.items():
                if doc_type == "specialist_plans":
                    continue
                output_lines.append(f"\n### {doc_type.replace('_', ' ').title()}")
                if isinstance(content, str):
                    summary = content[:200].replace("\n", " ").strip()
                    output_lines.append(f"{summary}...")

        output_lines.append(
            "\n\nUse read_planning with action='read_document' to read full documents."
        )

        return ToolResult(output="\n".join(output_lines))
