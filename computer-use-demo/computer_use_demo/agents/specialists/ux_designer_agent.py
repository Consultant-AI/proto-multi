"""
UX Designer Specialist Agent.

Expertise in:
- UI/UX design
- Visual design
- Interaction design
- Design systems
- Prototyping
- User research
"""

from typing import Any

from .base_specialist import BaseSpecialist


class UXDesignerAgent(BaseSpecialist):
    """UX Designer specialist focused on UI/UX and visual design."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None):
        """Initialize UX designer agent."""
        super().__init__(
            role="ux-designer",
            name="UX Designer Specialist",
            session_id=session_id,
            tools=tools,
        )

    def get_domain_expertise(self) -> str:
        """Get UX design domain expertise description."""
        return """UI/UX design, visual design, interaction design, design systems, prototyping,
wireframing, user research, accessibility (a11y), responsive design, design patterns,
typography, color theory, and user-centered design principles."""
