"""
Postmortem Agent.

Expertise in:
- Incident analysis
- Root cause identification
- Lessons learned
- Prevention recommendations
- Postmortem facilitation
- Action item tracking
"""

from typing import Any

from .base_specialist import BaseSpecialist


class PostmortemAgent(BaseSpecialist):
    """Postmortem specialist focused on incident analysis and lessons learned."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize Postmortem agent."""
        super().__init__(
            role="postmortem",
            name="Postmortem",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get Postmortem domain expertise description."""
        return """Incident postmortem facilitation, root cause analysis,
lessons learned documentation, prevention recommendation development,
blameless postmortem culture, action item identification and tracking,
pattern recognition across incidents, and systemic improvement proposals."""
