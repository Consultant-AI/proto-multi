"""
Deal Desk Agent.

Expertise in:
- Pricing approvals
- Contract packaging
- Deal structuring
- Discount management
- Custom terms
- Revenue recognition
"""

from typing import Any

from .base_specialist import BaseSpecialist


class DealDeskAgent(BaseSpecialist):
    """Deal Desk specialist focused on pricing approvals and contract packaging."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize deal desk agent."""
        super().__init__(
            role="deal-desk",
            name="Deal Desk Specialist",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get deal desk domain expertise description."""
        return """Pricing approvals, contract packaging, deal structuring, discount management,
custom terms evaluation, revenue recognition rules, multi-year deals,
enterprise pricing, volume discounts, deal review process, approval workflows,
pricing strategy, and contract templates."""
