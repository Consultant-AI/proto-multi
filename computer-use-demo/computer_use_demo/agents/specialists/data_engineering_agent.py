"""
Data Engineering Agent.

Expertise in:
- ETL/ELT pipelines
- Data warehousing
- Data governance
- Pipeline orchestration
- Data quality
- Schema management
"""

from typing import Any

from .base_specialist import BaseSpecialist


class DataEngineeringAgent(BaseSpecialist):
    """Data Engineering specialist focused on ETL/ELT, pipelines, warehouse, and governance."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize data engineering agent."""
        super().__init__(
            role="data-engineering",
            name="Data Engineering Specialist",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get data engineering domain expertise description."""
        return """ETL/ELT pipelines, data warehousing (Snowflake, BigQuery, Redshift), data governance,
pipeline orchestration (Airflow, Dagster), data quality frameworks, schema management,
data modeling, streaming data (Kafka), batch processing, data lake architecture,
CDC (change data capture), and data infrastructure."""
