"""
Prospecting Agent.

Expertise in:
- Lead list building
- Outreach sequences
- Personalization
- Cold outreach
- Multi-channel prospecting
- Response optimization
"""

from typing import Any

from .base_specialist import BaseSpecialist


class ProspectingAgent(BaseSpecialist):
    """Prospecting specialist focused on lists, outreach sequences, and personalization."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize prospecting agent."""
        super().__init__(
            role="prospecting",
            name="Prospecting Specialist",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get prospecting domain expertise description."""
        return """Lead list building, outreach sequences, message personalization, cold outreach,
multi-channel prospecting (email, LinkedIn, phone), response optimization,
sequence timing, A/B testing outreach, objection handling, follow-up cadences,
prospect research, and outbound sales strategy."""
