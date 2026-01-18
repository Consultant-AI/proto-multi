"""
CFO Agent.

Expertise in:
- Financial strategy
- Financial planning
- Budget management
- Financial reporting
- Investment decisions
- Financial leadership
"""

from typing import Any

from .base_specialist import BaseSpecialist


class CFOAgent(BaseSpecialist):
    """CFO specialist focused on financial strategy and leadership."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize CFO agent."""
        super().__init__(
            role="cfo",
            name="CFO",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get CFO domain expertise description."""
        return """Financial strategy, financial planning & analysis, budget management,
financial reporting, investment decisions, financial leadership, cash flow management,
fundraising strategy, financial modeling, unit economics, profitability analysis,
and cross-functional financial coordination."""
