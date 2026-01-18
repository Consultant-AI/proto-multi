"""
PR/Comms Agent.

Expertise in:
- Press releases
- Media outreach
- Crisis communications
- Thought leadership
- Press coverage
- Media relations
"""

from typing import Any

from .base_specialist import BaseSpecialist


class PRCommsAgent(BaseSpecialist):
    """PR/Comms specialist focused on press releases, media outreach, and crisis comms."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize PR/comms agent."""
        super().__init__(
            role="pr-comms",
            name="PR / Comms Specialist",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get PR/comms domain expertise description."""
        return """Press releases, media outreach, crisis communications, thought leadership,
press coverage tracking, media relations, spokesperson preparation, press kits,
media pitch creation, journalist relationships, earned media strategy,
announcement timing, and communications planning."""
