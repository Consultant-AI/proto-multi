"""
Meeting Agenda + Pre-read Agent.

Expertise in:
- Meeting preparation
- Agenda structuring
- Pre-read document creation
- Time allocation
- Discussion facilitation
- Meeting efficiency
"""

from typing import Any

from .base_specialist import BaseSpecialist


class MeetingAgendaAgent(BaseSpecialist):
    """Meeting agenda specialist focused on preparing effective meetings and pre-reads."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize Meeting Agenda agent."""
        super().__init__(
            role="meeting-agenda",
            name="Meeting Agenda",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get Meeting Agenda domain expertise description."""
        return """Meeting agenda creation and structuring, pre-read document preparation,
time allocation optimization, discussion topic prioritization, attendee preparation,
background material compilation, decision point identification,
meeting efficiency improvement, follow-up action planning,
and ensuring productive executive meetings."""
