"""
Metric Pack Builder Agent.

Expertise in:
- Metric package creation
- Dashboard assembly
- KPI bundling
- Metric documentation
- Reporting templates
- Data visualization specs
"""

from typing import Any

from .base_specialist import BaseSpecialist


class MetricPackAgent(BaseSpecialist):
    """Metric pack builder specialist focused on assembling metric packages and dashboards."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize Metric Pack agent."""
        super().__init__(
            role="metric-pack",
            name="Metric Pack Builder",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get Metric Pack Builder domain expertise description."""
        return """Metric package creation and assembly, dashboard specification,
KPI bundling for stakeholders, metric documentation,
reporting template design, data visualization requirements,
metric hierarchy organization, and stakeholder-specific metric views."""
