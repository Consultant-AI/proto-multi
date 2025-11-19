"""
Customer Success Specialist Agent.

Expertise in:
- Customer onboarding
- Account management
- Customer health monitoring
- Support escalation
- Retention strategies
- Success metrics
"""

from typing import Any

from .base_specialist import BaseSpecialist


class CustomerSuccessAgent(BaseSpecialist):
    """Customer Success specialist focused on customer satisfaction and retention."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None):
        """Initialize customer success agent."""
        super().__init__(
            role="customer-success",
            name="Customer Success Specialist",
            session_id=session_id,
            tools=tools,
        )

    def get_domain_expertise(self) -> str:
        """Get customer success domain expertise description."""
        return """Customer onboarding and training, account management, customer health monitoring and scoring,
support escalation management, retention and renewal strategies, customer success metrics (NPS, CSAT, churn),
customer advocacy and references, quarterly business reviews, expansion and upsell, customer feedback collection,
success planning, and relationship management."""
