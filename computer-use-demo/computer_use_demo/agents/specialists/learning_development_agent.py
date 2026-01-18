"""
Learning & Development Agent.

Expertise in:
- Training plans
- Internal courses
- Skill development
- Learning paths
- Knowledge sharing
- Professional growth
"""

from typing import Any

from .base_specialist import BaseSpecialist


class LearningDevelopmentAgent(BaseSpecialist):
    """Learning & Development specialist focused on training plans and internal courses."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize learning & development agent."""
        super().__init__(
            role="learning-development",
            name="Learning & Development Specialist",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get learning & development domain expertise description."""
        return """Training plans, internal courses, skill development programs, learning paths,
knowledge sharing, professional growth initiatives, LMS administration,
training content creation, mentorship programs, leadership development,
training effectiveness measurement, and continuous learning culture."""
