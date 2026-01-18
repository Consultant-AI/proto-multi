"""
CMO Agent.

Expertise in:
- Marketing strategy
- Brand management
- Growth marketing
- Demand generation
- Market positioning
- Marketing leadership
"""

from typing import Any

from .base_specialist import BaseSpecialist


class CMOAgent(BaseSpecialist):
    """CMO specialist focused on marketing strategy and brand leadership."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize CMO agent."""
        super().__init__(
            role="cmo",
            name="CMO",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get CMO domain expertise description."""
        return """Marketing strategy, brand management, growth marketing, demand generation,
market positioning, marketing leadership, campaign strategy, marketing budget allocation,
brand awareness, customer acquisition strategy, marketing analytics,
and cross-functional marketing coordination."""
