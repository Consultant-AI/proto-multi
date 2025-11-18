"""
Marketing Specialist Agent.

Expertise in:
- Marketing strategy
- Brand development
- Campaign planning
- Content marketing
- SEO/SEM
- Analytics and metrics
"""

from typing import Any

from .base_specialist import BaseSpecialist


class MarketingAgent(BaseSpecialist):
    """Marketing specialist focused on marketing strategy and execution."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None):
        """Initialize marketing agent."""
        super().__init__(
            role="marketing",
            name="Marketing Specialist",
            session_id=session_id,
            tools=tools,
        )

    def get_domain_expertise(self) -> str:
        """Get marketing domain expertise description."""
        return """Marketing strategy, brand development, campaign planning, content marketing,
SEO/SEM, social media marketing, email marketing, analytics, conversion optimization,
customer acquisition, retention strategies, and marketing automation."""
