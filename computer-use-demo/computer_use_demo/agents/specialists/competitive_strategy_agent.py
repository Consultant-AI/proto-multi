"""
Competitive Strategy Agent.

Expertise in:
- Competitive analysis
- Market positioning
- Competitive intelligence
- Strategic differentiation
- Competitive response
- Market dynamics
"""

from typing import Any

from .base_specialist import BaseSpecialist


class CompetitiveStrategyAgent(BaseSpecialist):
    """Competitive strategy specialist focused on competitive positioning and analysis."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize Competitive Strategy agent."""
        super().__init__(
            role="competitive-strategy",
            name="Competitive Strategy",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get Competitive Strategy domain expertise description."""
        return """Competitive analysis and intelligence, market positioning strategy,
strategic differentiation development, competitive response planning,
market dynamics assessment, competitor capability mapping,
competitive advantage identification, win/loss analysis,
and strategic moat building."""
