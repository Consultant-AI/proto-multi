"""
CTO Agent.

Expertise in:
- Technology strategy
- Engineering leadership
- Architecture decisions
- Technical vision
- Innovation
- R&D direction
"""

from typing import Any

from .base_specialist import BaseSpecialist


class CTOAgent(BaseSpecialist):
    """CTO specialist focused on technology strategy and engineering leadership."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize CTO agent."""
        super().__init__(
            role="cto",
            name="CTO",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get CTO domain expertise description."""
        return """Technology strategy, engineering leadership, architecture decisions,
technical vision, innovation direction, R&D strategy, build vs buy decisions,
technology stack selection, technical debt management, engineering culture,
scalability planning, and cross-functional technical coordination."""
