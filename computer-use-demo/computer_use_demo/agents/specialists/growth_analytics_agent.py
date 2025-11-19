"""
Growth Analytics Specialist Agent.

Expertise in:
- Growth experimentation
- Funnel optimization
- User acquisition
- Retention analysis
- Growth metrics
- A/B testing
"""

from typing import Any

from .base_specialist import BaseSpecialist


class GrowthAnalyticsAgent(BaseSpecialist):
    """Growth Analytics specialist focused on data-driven growth strategies."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None):
        """Initialize growth analytics agent."""
        super().__init__(
            role="growth-analytics",
            name="Growth Analytics Specialist",
            session_id=session_id,
            tools=tools,
        )

    def get_domain_expertise(self) -> str:
        """Get growth analytics domain expertise description."""
        return """Growth experimentation and testing, funnel optimization and conversion rate optimization (CRO),
user acquisition strategies, retention and engagement analysis, growth metrics (activation, retention, referral),
A/B testing and multivariate testing, cohort analysis, product-led growth, viral growth mechanics,
growth modeling and forecasting, and data-driven growth strategies."""
