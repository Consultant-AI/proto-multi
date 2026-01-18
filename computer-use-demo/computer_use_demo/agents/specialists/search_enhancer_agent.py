"""
Search Enhancer Agent.

Expertise in:
- Search optimization
- Relevance tuning
- Query understanding
- Search analytics
- Synonym management
- Result ranking
"""

from typing import Any

from .base_specialist import BaseSpecialist


class SearchEnhancerAgent(BaseSpecialist):
    """Search enhancer specialist focused on improving internal search quality."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize Search Enhancer agent."""
        super().__init__(
            role="search-enhancer",
            name="Search Enhancer",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get Search Enhancer domain expertise description."""
        return """Search optimization and relevance tuning, query understanding improvement,
search analytics and insights, synonym and alias management,
result ranking optimization, zero-result query resolution,
search performance monitoring, and findability enhancement."""
