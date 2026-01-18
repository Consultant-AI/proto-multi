"""
OKR Coach Agent.

Expertise in:
- OKR framework implementation
- Objective setting
- Key result definition
- Goal alignment
- Progress tracking
- OKR facilitation
"""

from typing import Any

from .base_specialist import BaseSpecialist


class OKRCoachAgent(BaseSpecialist):
    """OKR coach specialist focused on objectives and key results framework."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize OKR Coach agent."""
        super().__init__(
            role="okr-coach",
            name="OKR Coach",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get OKR Coach domain expertise description."""
        return """OKR framework implementation and coaching, objective setting best practices,
key result definition and measurement, goal alignment across teams,
OKR progress tracking and scoring, quarterly planning facilitation,
cascade alignment verification, stretch goal calibration,
and continuous OKR improvement."""
