"""
Brand Agent.

Expertise in:
- Brand voice
- Brand guidelines
- Brand consistency
- Visual identity
- Brand messaging
- Brand strategy
"""

from typing import Any

from .base_specialist import BaseSpecialist


class BrandAgent(BaseSpecialist):
    """Brand specialist focused on voice, guidelines, and consistency."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize brand agent."""
        super().__init__(
            role="brand",
            name="Brand Specialist",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get brand domain expertise description."""
        return """Brand voice development, brand guidelines, brand consistency enforcement,
visual identity management, brand messaging, brand strategy, tone of voice,
brand positioning, brand architecture, brand storytelling, brand audits,
brand refresh, and brand asset management."""
