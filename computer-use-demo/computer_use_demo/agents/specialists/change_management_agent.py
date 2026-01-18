"""
Change Management Agent.

Expertise in:
- Change planning
- Impact assessment
- Stakeholder preparation
- Communication planning
- Adoption management
- Change tracking
"""

from typing import Any

from .base_specialist import BaseSpecialist


class ChangeManagementAgent(BaseSpecialist):
    """Change management specialist focused on organizational change planning and execution."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize Change Management agent."""
        super().__init__(
            role="change-management",
            name="Change Management",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get Change Management domain expertise description."""
        return """Change planning and execution, impact assessment,
stakeholder preparation and engagement, communication planning,
change adoption management, resistance management,
training coordination, change tracking and measurement,
and organizational readiness assessment."""
