"""
Update Planning Document Tool for Proto Multi-Agent System.

Enables specialist agents to update shared planning documents.
"""

from ...proto_logging import get_logger
from ...planning import ProjectManager
from ..base import BaseAnthropicTool, CLIResult, ToolError, ToolResult


class UpdatePlanningDocTool(BaseAnthropicTool):
    """
    Tool for updating shared planning documents.

    This tool allows specialist agents to:
    1. Add implementation notes to TECHNICAL_SPEC.md
    2. Mark tasks complete in ROADMAP.md
    3. Document decisions in DECISIONS.md
    4. Add learnings to KNOWLEDGE_BASE.md
    """

    name: str = "update_planning_document"
    api_type: str = "custom"

    def to_params(self):
        """Return tool parameter schema for Anthropic API."""
        return {
            "name": self.name,
            "description": """Update shared planning documents with your contributions.

Use this tool to:
- Add implementation notes to TECHNICAL_SPEC.md
- Document technical decisions
- Mark tasks as completed
- Share learnings with other specialists

All specialists work from the SAME planning documents, so your updates
will be visible to the CEO and other specialists.""",
            "input_schema": {
                "type": "object",
                "properties": {
                    "project_name": {
                        "type": "string",
                        "description": "Name of the project",
                    },
                    "document_type": {
                        "type": "string",
                        "enum": ["technical_spec", "knowledge_base", "decisions"],
                        "description": "Which planning document to update",
                    },
                    "update_content": {
                        "type": "string",
                        "description": "Content to add to the document (will be appended)",
                    },
                    "section_title": {
                        "type": "string",
                        "description": "Optional section title for the update",
                    },
                },
                "required": ["project_name", "document_type", "update_content"],
            },
        }

    async def __call__(
        self,
        project_name: str,
        document_type: str,
        update_content: str,
        section_title: str | None = None,
        **kwargs,
    ) -> ToolResult | CLIResult:
        """
        Update a shared planning document.

        Args:
            project_name: Project name
            document_type: Which document to update
            update_content: Content to add
            section_title: Optional section title

        Returns:
            ToolResult with confirmation
        """
        logger = get_logger()

        try:
            project_manager = ProjectManager()

            # Check if project exists
            if not project_manager.project_exists(project_name):
                return ToolResult(error=f"Project '{project_name}' does not exist")

            # Load existing document
            existing_content = project_manager.load_document(project_name, document_type)  # type: ignore

            if not existing_content:
                existing_content = f"# {document_type.replace('_', ' ').title()}\n\n"

            # Format the update
            update_section = f"\n\n"
            if section_title:
                update_section += f"## {section_title}\n\n"
            update_section += update_content + "\n"

            # Append to document
            updated_content = existing_content + update_section

            # Save updated document
            doc_path = project_manager.save_document(
                project_name, document_type, updated_content  # type: ignore
            )

            logger.log_event(
                event_type="planning_document_updated",
                session_id="update-plan-tool",
                data={
                    "project_name": project_name,
                    "document_type": document_type,
                    "section_title": section_title,
                    "update_length": len(update_content),
                },
            )

            output = f"✓ Updated {document_type.upper()} for project '{project_name}'"
            if section_title:
                output += f"\n  Added section: {section_title}"
            output += f"\n  Path: {doc_path}"
            output += f"\n\nThis update is now visible to all specialists working on this project."

            return ToolResult(output=output)

        except Exception as e:
            logger.log_error("update-plan-tool", e)
            raise ToolError(f"Failed to update planning document: {str(e)}")
