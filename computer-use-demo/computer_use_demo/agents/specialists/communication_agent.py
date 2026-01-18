"""
Internal Communication Agent.

Expertise in:
- Internal communications
- Company announcements
- Employee messaging
- Communication channels
- Information distribution
- Message crafting
"""

from typing import Any

from .base_specialist import BaseSpecialist


class CommunicationAgent(BaseSpecialist):
    """Communication specialist focused on internal company communications."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize Communication agent."""
        super().__init__(
            role="communication",
            name="Internal Communication",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get Internal Communication domain expertise description."""
        return """Internal communications strategy, company announcement crafting,
employee messaging and engagement, communication channel management,
information distribution planning, message timing and targeting,
crisis communication support, and cross-functional communication coordination."""
