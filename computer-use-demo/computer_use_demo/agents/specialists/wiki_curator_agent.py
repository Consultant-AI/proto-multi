"""
Wiki Curator Agent.

Expertise in:
- Knowledge curation
- Wiki maintenance
- Content organization
- Information architecture
- Documentation quality
- Knowledge freshness
"""

from typing import Any

from .base_specialist import BaseSpecialist


class WikiCuratorAgent(BaseSpecialist):
    """Wiki curator specialist focused on maintaining and organizing internal wiki content."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize Wiki Curator agent."""
        super().__init__(
            role="wiki-curator",
            name="Wiki Curator",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get Wiki Curator domain expertise description."""
        return """Knowledge curation and organization, wiki content maintenance,
information architecture design, documentation quality assurance,
content freshness verification, duplicate content identification,
navigation improvement, and searchability optimization."""
