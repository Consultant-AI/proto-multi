"""
Cost Optimization Agent.

Expertise in:
- Resource rightsizing
- Waste detection
- Budget management
- Cloud cost analysis
- Reserved capacity
- Cost allocation
"""

from typing import Any

from .base_specialist import BaseSpecialist


class CostOptimizationAgent(BaseSpecialist):
    """Cost Optimization specialist focused on rightsizing, waste detection, and budget caps."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize cost optimization agent."""
        super().__init__(
            role="cost-optimization",
            name="Cost Optimization Specialist",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get cost optimization domain expertise description."""
        return """Resource rightsizing, waste detection, budget management, cloud cost analysis,
reserved capacity planning, cost allocation, spot instances, savings plans,
cost anomaly detection, FinOps practices, cost dashboards, resource tagging,
idle resource identification, and cost forecasting."""
