"""
Marketing Strategy Specialist Agent.

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


class MarketingStrategyAgent(BaseSpecialist):
    """Marketing strategy specialist focused on strategic marketing planning and execution."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize marketing strategy agent."""
        super().__init__(
            role="marketing-strategy",
            name="Marketing Strategy Specialist",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get marketing strategy domain expertise description."""
        return """Marketing strategy, brand development, campaign planning, content marketing,
SEO/SEM, social media marketing, email marketing, analytics, conversion optimization,
customer acquisition, retention strategies, and marketing automation."""
