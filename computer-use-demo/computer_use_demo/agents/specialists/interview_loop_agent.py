"""
Interview Loop Agent.

Expertise in:
- Interview scorecards
- Calibration sessions
- Decision memos
- Interview design
- Hiring decisions
- Feedback synthesis
"""

from typing import Any

from .base_specialist import BaseSpecialist


class InterviewLoopAgent(BaseSpecialist):
    """Interview Loop specialist focused on scorecards, calibration, and decision memos."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize interview loop agent."""
        super().__init__(
            role="interview-loop",
            name="Interview Loop Specialist",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get interview loop domain expertise description."""
        return """Interview scorecards, calibration sessions, decision memos, interview design,
hiring decisions support, feedback synthesis, interview training, structured interviews,
competency assessment, hiring bar calibration, debrief facilitation,
and interview process optimization."""
