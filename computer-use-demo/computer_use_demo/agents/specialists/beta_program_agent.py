"""
Beta Program Manager Agent.

Expertise in:
- Beta program management
- Early access programs
- Beta user recruitment
- Feedback collection
- Beta analytics
- Launch readiness
"""

from typing import Any

from .base_specialist import BaseSpecialist


class BetaProgramAgent(BaseSpecialist):
    """Beta program manager specialist focused on managing beta and early access programs."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize Beta Program agent."""
        super().__init__(
            role="beta-program",
            name="Beta Program Manager",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get Beta Program Manager domain expertise description."""
        return """Beta program management and coordination, early access program design,
beta user recruitment and selection, feedback collection and synthesis,
beta analytics and success metrics, launch readiness assessment,
beta-to-GA transition planning, and beta user communication."""
