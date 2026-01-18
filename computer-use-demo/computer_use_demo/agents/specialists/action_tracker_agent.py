"""
Action Items + Follow-up Tracker Agent.

Expertise in:
- Action item tracking
- Follow-up management
- Accountability systems
- Deadline monitoring
- Progress tracking
- Commitment management
"""

from typing import Any

from .base_specialist import BaseSpecialist


class ActionTrackerAgent(BaseSpecialist):
    """Action tracker specialist focused on tracking commitments and ensuring follow-through."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize Action Tracker agent."""
        super().__init__(
            role="action-tracker",
            name="Action Tracker",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get Action Tracker domain expertise description."""
        return """Action item tracking and management, follow-up scheduling and reminders,
accountability system maintenance, deadline monitoring and escalation,
progress tracking across initiatives, commitment management,
meeting action extraction, stakeholder follow-up coordination,
and ensuring organizational follow-through on decisions."""
