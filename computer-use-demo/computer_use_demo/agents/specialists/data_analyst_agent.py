"""
Data Analyst Specialist Agent.

Expertise in:
- Data analysis and visualization
- SQL and database querying
- Business intelligence
- Metrics and KPIs
- Statistical analysis
- Data reporting
"""

from typing import Any

from .base_specialist import BaseSpecialist


class DataAnalystAgent(BaseSpecialist):
    """Data Analyst specialist focused on data analysis and insights."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize data analyst agent."""
        super().__init__(
            role="data-analyst",
            name="Data Analyst Specialist",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get data analysis domain expertise description."""
        return """Data analysis and visualization, SQL and database querying, business intelligence,
metrics and KPIs definition, statistical analysis, data reporting and dashboards, A/B testing analysis,
cohort analysis, funnel analysis, data modeling, Python/R for data science, data quality and validation,
and data-driven decision making."""
