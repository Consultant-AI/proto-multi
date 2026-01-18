"""
Knowledge Base Agent.

Expertise in:
- Article creation
- KB maintenance
- FAQ development
- Search optimization
- Content organization
- Self-service enablement
"""

from typing import Any

from .base_specialist import BaseSpecialist


class KnowledgeBaseAgent(BaseSpecialist):
    """Knowledge Base specialist focused on turning tickets into docs and keeping KB current."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize knowledge base agent."""
        super().__init__(
            role="knowledge-base",
            name="Knowledge Base Specialist",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get knowledge base domain expertise description."""
        return """Article creation from support tickets, KB maintenance, FAQ development,
search optimization, content organization, self-service enablement, article templates,
content freshness, KB analytics, article feedback, documentation standards,
multimedia guides, and knowledge gap identification."""
