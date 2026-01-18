"""
Vision Keeper Agent.

Expertise in:
- Company vision alignment
- Mission articulation
- Long-term direction
- Strategic narrative
- Purpose communication
- Values reinforcement
"""

from typing import Any

from .base_specialist import BaseSpecialist


class VisionKeeperAgent(BaseSpecialist):
    """Vision keeper specialist focused on maintaining and communicating company vision."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize Vision Keeper agent."""
        super().__init__(
            role="vision-keeper",
            name="Vision Keeper",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get Vision Keeper domain expertise description."""
        return """Company vision maintenance and articulation, mission alignment verification,
long-term strategic direction, strategic narrative development, purpose communication,
values reinforcement, vision-to-action translation, stakeholder vision alignment,
and ensuring organizational decisions align with core vision."""
