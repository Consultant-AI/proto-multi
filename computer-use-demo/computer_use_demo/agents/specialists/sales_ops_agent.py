"""
Sales Ops Agent.

Expertise in:
- CRM hygiene
- Territory management
- Pipeline analytics
- Sales forecasting
- Process optimization
- Sales reporting
"""

from typing import Any

from .base_specialist import BaseSpecialist


class SalesOpsAgent(BaseSpecialist):
    """Sales Ops specialist focused on CRM hygiene, territories, and pipeline analytics."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize sales ops agent."""
        super().__init__(
            role="sales-ops",
            name="Sales Ops Specialist",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get sales ops domain expertise description."""
        return """CRM hygiene and administration, territory management, pipeline analytics,
sales forecasting, process optimization, sales reporting, quota setting,
commission calculations, sales tool administration, data quality,
sales metrics, and operational efficiency."""
