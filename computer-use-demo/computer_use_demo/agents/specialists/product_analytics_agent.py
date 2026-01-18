"""
Product Analytics Agent.

Expertise in:
- Product metrics
- Usage analytics
- Feature adoption
- Funnel analysis
- Cohort analysis
- Product insights
"""

from typing import Any

from .base_specialist import BaseSpecialist


class ProductAnalyticsAgent(BaseSpecialist):
    """Product analytics specialist focused on product usage and metrics analysis."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize Product Analytics agent."""
        super().__init__(
            role="product-analytics",
            name="Product Analytics",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get Product Analytics domain expertise description."""
        return """Product metrics analysis, usage pattern identification,
feature adoption tracking, funnel analysis and optimization,
cohort analysis, retention analysis, product-led growth metrics,
user behavior insights, and data-driven product recommendations."""
