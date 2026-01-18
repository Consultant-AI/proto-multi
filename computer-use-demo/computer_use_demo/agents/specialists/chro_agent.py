"""
CHRO Agent.

Expertise in:
- People strategy
- Talent management
- Culture development
- Employee experience
- HR operations
- People leadership
"""

from typing import Any

from .base_specialist import BaseSpecialist


class CHROAgent(BaseSpecialist):
    """CHRO specialist focused on people strategy and talent management."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize CHRO agent."""
        super().__init__(
            role="chro",
            name="CHRO",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get CHRO domain expertise description."""
        return """People strategy, talent management, culture development, employee experience,
HR operations, people leadership, organizational design, workforce planning,
diversity & inclusion, employer branding, compensation strategy,
and cross-functional people coordination."""
