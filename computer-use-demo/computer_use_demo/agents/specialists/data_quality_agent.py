"""
Data Quality Agent.

Expertise in:
- Data lineage
- Data testing
- Anomaly detection
- Data backfills
- Quality metrics
- Data validation
"""

from typing import Any

from .base_specialist import BaseSpecialist


class DataQualityAgent(BaseSpecialist):
    """Data Quality specialist focused on lineage, tests, anomaly detection, and backfills."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize data quality agent."""
        super().__init__(
            role="data-quality",
            name="Data Quality Specialist",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get data quality domain expertise description."""
        return """Data lineage tracking, data testing (dbt tests, Great Expectations), anomaly detection,
data backfills, quality metrics, data validation, schema validation, freshness checks,
completeness checks, consistency checks, data profiling, data quality dashboards,
data contracts, and data quality alerting."""
