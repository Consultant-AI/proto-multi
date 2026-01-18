"""
CPO Agent.

Expertise in:
- Product vision
- Product strategy
- Roadmap planning
- User experience
- Market fit
- Product leadership
"""

from typing import Any

from .base_specialist import BaseSpecialist


class CPOAgent(BaseSpecialist):
    """CPO specialist focused on product vision and strategy."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize CPO agent."""
        super().__init__(
            role="cpo",
            name="CPO",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get CPO domain expertise description."""
        return """Product vision, product strategy, roadmap planning, user experience leadership,
product-market fit, product leadership, feature prioritization, product metrics,
customer insights synthesis, competitive positioning, product lifecycle management,
and cross-functional product coordination."""
