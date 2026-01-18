"""
CDO Agent.

Expertise in:
- Data strategy
- Analytics leadership
- Data governance
- Business intelligence
- Data-driven decisions
- ML/AI strategy
"""

from typing import Any

from .base_specialist import BaseSpecialist


class CDOAgent(BaseSpecialist):
    """CDO specialist focused on data strategy and analytics leadership."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize CDO agent."""
        super().__init__(
            role="cdo",
            name="CDO",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get CDO domain expertise description."""
        return """Data strategy, analytics leadership, data governance, business intelligence,
data-driven decision making, ML/AI strategy, data architecture, data quality standards,
data privacy compliance, analytics roadmap, data democratization,
and cross-functional data coordination."""
