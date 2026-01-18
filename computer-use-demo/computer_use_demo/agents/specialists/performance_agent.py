"""
Performance Agent.

Expertise in:
- Performance reviews
- Goal setting
- Feedback cycles
- Performance improvement
- Career development
- Performance metrics
"""

from typing import Any

from .base_specialist import BaseSpecialist


class PerformanceAgent(BaseSpecialist):
    """Performance specialist focused on reviews, goals, and feedback cycles."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize performance agent."""
        super().__init__(
            role="performance",
            name="Performance Specialist",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get performance domain expertise description."""
        return """Performance reviews, goal setting (OKRs, KPIs), feedback cycles,
performance improvement plans, career development planning, performance metrics,
360 feedback, self-assessments, manager feedback, calibration,
continuous feedback, and performance documentation."""
