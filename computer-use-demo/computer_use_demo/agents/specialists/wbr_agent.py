"""
WBR (Weekly Business Review) Agent.

Expertise in:
- Weekly reviews
- Business metrics review
- Performance summaries
- Week-over-week analysis
- Executive briefings
- Operational reviews
"""

from typing import Any

from .base_specialist import BaseSpecialist


class WBRAgent(BaseSpecialist):
    """WBR specialist focused on weekly business review preparation and analysis."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize WBR agent."""
        super().__init__(
            role="wbr",
            name="Weekly Business Review",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get WBR domain expertise description."""
        return """Weekly business review preparation and facilitation, business metrics analysis,
week-over-week performance comparison, executive summary preparation,
operational review coordination, KPI trend identification,
action item tracking from reviews, and cross-functional alignment verification."""
