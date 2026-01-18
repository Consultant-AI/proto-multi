"""
Partner/Channel Agent.

Expertise in:
- Reseller management
- Alliance partnerships
- Co-marketing
- Partner programs
- Channel strategy
- Partner enablement
"""

from typing import Any

from .base_specialist import BaseSpecialist


class PartnerChannelAgent(BaseSpecialist):
    """Partner/Channel specialist focused on resellers, alliances, and co-marketing."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize partner/channel agent."""
        super().__init__(
            role="partner-channel",
            name="Partner / Channel Specialist",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get partner/channel domain expertise description."""
        return """Reseller management, alliance partnerships, co-marketing initiatives,
partner programs, channel strategy, partner enablement, partner onboarding,
deal registration, partner portal management, partner incentives, referral programs,
integration partnerships, and partner performance tracking."""
