"""
Revenue Ops Agent.

Expertise in:
- Pricing management
- Billing plans
- Billing logic
- Refunds
- Revenue operations
- Subscription management
"""

from typing import Any

from .base_specialist import BaseSpecialist


class RevenueOpsAgent(BaseSpecialist):
    """Revenue Ops specialist focused on pricing, plans, billing logic, and refunds."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize revenue ops agent."""
        super().__init__(
            role="revenue-ops",
            name="Revenue Ops Specialist",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get revenue ops domain expertise description."""
        return """Pricing management, billing plans, billing logic, refund processing,
revenue operations, subscription management, usage-based billing, proration,
plan changes, trial management, payment failures, dunning management,
revenue recognition, and billing system configuration."""
