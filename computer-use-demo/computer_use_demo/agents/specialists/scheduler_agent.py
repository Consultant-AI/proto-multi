"""
Scheduler Agent.

Expertise in:
- Calendar management
- Time-boxing
- Prioritization queues
- Resource scheduling
- Meeting coordination
- Capacity planning
"""

from typing import Any

from .base_specialist import BaseSpecialist


class SchedulerAgent(BaseSpecialist):
    """Scheduler specialist focused on time management and prioritization."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize scheduler agent."""
        super().__init__(
            role="scheduler",
            name="Scheduler Specialist",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get scheduler domain expertise description."""
        return """Calendar management, time-boxing, prioritization queues, resource scheduling,
meeting coordination, capacity planning, deadline management, workload balancing,
availability tracking, scheduling optimization, time allocation, sprint planning,
blocking time for deep work, and scheduling conflict resolution."""
