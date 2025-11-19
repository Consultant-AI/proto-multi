"""
Admin Coordinator Specialist Agent.

Expertise in:
- Administrative coordination
- Meeting management
- Communication coordination
- Document organization
- Task tracking
- Executive support
"""

from typing import Any

from .base_specialist import BaseSpecialist


class AdminCoordinatorAgent(BaseSpecialist):
    """Admin Coordinator specialist focused on administrative support and coordination."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None):
        """Initialize admin coordinator agent."""
        super().__init__(
            role="admin-coordinator",
            name="Admin Coordinator Specialist",
            session_id=session_id,
            tools=tools,
        )

    def get_domain_expertise(self) -> str:
        """Get admin coordinator domain expertise description."""
        return """Administrative coordination and support, meeting scheduling and management, communication coordination,
document organization and management, task tracking and follow-up, executive support and assistance,
calendar management, travel coordination, expense tracking, internal communications, event planning,
and office operations."""
