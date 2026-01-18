"""
KPI Definition Agent.

Expertise in:
- KPI framework design
- Metric definition
- Performance indicators
- Measurement systems
- Dashboard design
- Success criteria
"""

from typing import Any

from .base_specialist import BaseSpecialist


class KPIDefinitionAgent(BaseSpecialist):
    """KPI definition specialist focused on designing meaningful performance metrics."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize KPI Definition agent."""
        super().__init__(
            role="kpi-definition",
            name="KPI Definition",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get KPI Definition domain expertise description."""
        return """KPI framework design and implementation, metric definition and selection,
leading vs lagging indicator identification, measurement system design,
dashboard specification, success criteria establishment,
benchmark setting, metric hierarchy design,
and ensuring KPIs drive desired behaviors."""
