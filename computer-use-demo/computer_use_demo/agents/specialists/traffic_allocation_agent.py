"""
Traffic Allocation Agent.

Expertise in:
- Traffic splitting
- User segmentation
- Rollout percentages
- Allocation strategies
- Ramping plans
- Traffic management
"""

from typing import Any

from .base_specialist import BaseSpecialist


class TrafficAllocationAgent(BaseSpecialist):
    """Traffic allocation specialist focused on experiment traffic management."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize Traffic Allocation agent."""
        super().__init__(
            role="traffic-allocation",
            name="Traffic Allocation",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get Traffic Allocation domain expertise description."""
        return """Traffic splitting and allocation, user segmentation for experiments,
rollout percentage planning, allocation strategy design,
gradual ramping plans, traffic management during experiments,
holdout group management, and allocation conflict resolution."""
