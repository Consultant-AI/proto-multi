"""
Resource Allocation Agent.

Expertise in:
- Resource planning
- Budget allocation
- Headcount planning
- Capacity management
- Investment prioritization
- Resource optimization
"""

from typing import Any

from .base_specialist import BaseSpecialist


class ResourceAllocationAgent(BaseSpecialist):
    """Resource allocation specialist focused on optimal distribution of resources."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize Resource Allocation agent."""
        super().__init__(
            role="resource-allocation",
            name="Resource Allocation",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get Resource Allocation domain expertise description."""
        return """Resource planning and allocation, budget distribution optimization,
headcount planning and forecasting, capacity management,
investment prioritization frameworks, resource constraint analysis,
cross-team resource balancing, utilization optimization,
and strategic resource deployment."""
