"""
Paid Acquisition Agent.

Expertise in:
- Ad campaign management
- Budget allocation
- Creative testing
- Audience targeting
- Bid optimization
- Attribution
"""

from typing import Any

from .base_specialist import BaseSpecialist


class PaidAcquisitionAgent(BaseSpecialist):
    """Paid Acquisition specialist focused on ads, budget allocation, and creative testing."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize paid acquisition agent."""
        super().__init__(
            role="paid-acquisition",
            name="Paid Acquisition Specialist",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get paid acquisition domain expertise description."""
        return """Ad campaign management (Google Ads, Facebook Ads, LinkedIn Ads), budget allocation,
creative testing, audience targeting, bid optimization, attribution modeling,
retargeting campaigns, lookalike audiences, conversion tracking, ROAS optimization,
ad copy writing, landing page optimization, and campaign reporting."""
