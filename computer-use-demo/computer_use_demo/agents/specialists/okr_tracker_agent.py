"""
OKR Tracker Agent.

Expertise in:
- OKR progress monitoring
- Key result tracking
- Goal completion analysis
- Progress reporting
- OKR dashboard management
- Quarterly reviews
"""

from typing import Any

from .base_specialist import BaseSpecialist


class OKRTrackerAgent(BaseSpecialist):
    """OKR tracker specialist focused on monitoring and reporting OKR progress."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize OKR Tracker agent."""
        super().__init__(
            role="okr-tracker",
            name="OKR Tracker",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get OKR Tracker domain expertise description."""
        return """OKR progress monitoring and tracking, key result completion analysis,
goal progress reporting, OKR dashboard management, quarterly review preparation,
at-risk objective identification, progress trend analysis,
cross-team OKR alignment verification, and automated progress updates."""
