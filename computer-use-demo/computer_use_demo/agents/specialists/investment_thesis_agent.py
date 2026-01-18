"""
Investment Thesis Agent.

Expertise in:
- Investment strategy
- Thesis development
- Growth investment
- Capital allocation
- Investment criteria
- Portfolio strategy
"""

from typing import Any

from .base_specialist import BaseSpecialist


class InvestmentThesisAgent(BaseSpecialist):
    """Investment thesis specialist focused on investment strategy and capital allocation."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize Investment Thesis agent."""
        super().__init__(
            role="investment-thesis",
            name="Investment Thesis",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get Investment Thesis domain expertise description."""
        return """Investment thesis development, capital allocation strategy,
growth investment evaluation, investment criteria definition,
portfolio strategy design, M&A thesis development,
strategic investment assessment, ROI framework design,
and investment decision support."""
