"""
Partnership Strategy Agent.

Expertise in:
- Partnership development
- Strategic alliances
- Partner ecosystem
- Joint ventures
- Partnership governance
- Alliance management
"""

from typing import Any

from .base_specialist import BaseSpecialist


class PartnershipStrategyAgent(BaseSpecialist):
    """Partnership strategy specialist focused on strategic alliances and partnerships."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize Partnership Strategy agent."""
        super().__init__(
            role="partnership-strategy",
            name="Partnership Strategy",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get Partnership Strategy domain expertise description."""
        return """Partnership development and strategy, strategic alliance formation,
partner ecosystem design, joint venture evaluation,
partnership governance frameworks, alliance management,
partner value assessment, partnership negotiation support,
and ecosystem partnership orchestration."""
