"""
SEO Agent.

Expertise in:
- Keyword strategy
- On-page optimization
- Technical SEO
- Link building
- Search analytics
- Content optimization
"""

from typing import Any

from .base_specialist import BaseSpecialist


class SEOAgent(BaseSpecialist):
    """SEO specialist focused on keyword strategy, on-page, and technical SEO."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize SEO agent."""
        super().__init__(
            role="seo",
            name="SEO Specialist",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get SEO domain expertise description."""
        return """Keyword strategy, on-page optimization, technical SEO, link building,
search analytics, content optimization for search, meta tags, structured data,
site architecture for SEO, page speed optimization, mobile SEO, local SEO,
SEO audits, rank tracking, and search algorithm understanding."""
