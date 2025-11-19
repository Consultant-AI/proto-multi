"""
Technical Writer Specialist Agent.

Expertise in:
- Documentation strategy
- API documentation
- User guides
- Internal docs
- Knowledge management
- Technical communication
"""

from typing import Any

from .base_specialist import BaseSpecialist


class TechnicalWriterAgent(BaseSpecialist):
    """Technical Writer specialist focused on documentation and technical communication."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None):
        """Initialize technical writer agent."""
        super().__init__(
            role="technical-writer",
            name="Technical Writer Specialist",
            session_id=session_id,
            tools=tools,
        )

    def get_domain_expertise(self) -> str:
        """Get technical writing domain expertise description."""
        return """Documentation strategy, API documentation (OpenAPI, Swagger), user guides and tutorials,
internal documentation, knowledge base management, technical communication, developer documentation,
release notes, README files, code comments and docstrings, documentation tools (Markdown, Sphinx, Docusaurus),
information architecture, and technical editing."""
