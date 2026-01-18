"""
CRO Agent.

Expertise in:
- Revenue strategy
- Sales leadership
- Pipeline management
- Revenue operations
- Go-to-market
- Sales excellence
"""

from typing import Any

from .base_specialist import BaseSpecialist


class CROAgent(BaseSpecialist):
    """CRO specialist focused on revenue strategy and sales leadership."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize CRO agent."""
        super().__init__(
            role="cro",
            name="CRO",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get CRO domain expertise description."""
        return """Revenue strategy, sales leadership, pipeline management, revenue operations,
go-to-market strategy, sales excellence, quota planning, territory management,
sales forecasting, revenue growth, customer acquisition cost optimization,
and cross-functional revenue coordination."""
