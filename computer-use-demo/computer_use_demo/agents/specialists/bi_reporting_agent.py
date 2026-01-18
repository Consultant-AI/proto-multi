"""
BI/Reporting Agent.

Expertise in:
- Executive reports
- Business reviews
- Dashboard creation
- KPI tracking
- Data visualization
- Report automation
"""

from typing import Any

from .base_specialist import BaseSpecialist


class BIReportingAgent(BaseSpecialist):
    """BI/Reporting specialist focused on exec reports, weekly business reviews, and dashboards."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize BI/reporting agent."""
        super().__init__(
            role="bi-reporting",
            name="BI / Reporting Specialist",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get BI/reporting domain expertise description."""
        return """Executive reports, weekly business reviews, dashboard creation (Tableau, Looker, Mode),
KPI tracking, data visualization, report automation, self-service analytics,
metric definitions, report scheduling, stakeholder communication, data storytelling,
ad-hoc analysis, and business intelligence strategy."""
