"""
Recruiting Agent.

Expertise in:
- Candidate sourcing
- Resume screening
- Interview scheduling
- Job postings
- Talent pipeline
- Recruiting strategy
"""

from typing import Any

from .base_specialist import BaseSpecialist


class RecruitingAgent(BaseSpecialist):
    """Recruiting specialist focused on sourcing, screening, and scheduling."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize recruiting agent."""
        super().__init__(
            role="recruiting",
            name="Recruiting Specialist",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get recruiting domain expertise description."""
        return """Candidate sourcing, resume screening, interview scheduling, job postings,
talent pipeline management, recruiting strategy, employer branding, candidate outreach,
ATS management, sourcing channels, diversity recruiting, candidate experience,
and recruiting metrics."""
