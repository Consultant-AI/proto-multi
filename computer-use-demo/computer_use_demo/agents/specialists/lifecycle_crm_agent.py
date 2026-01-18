"""
Lifecycle/CRM Agent.

Expertise in:
- Onboarding emails
- Reactivation campaigns
- Customer segmentation
- Email automation
- Customer journeys
- Retention marketing
"""

from typing import Any

from .base_specialist import BaseSpecialist


class LifecycleCRMAgent(BaseSpecialist):
    """Lifecycle/CRM specialist focused on onboarding emails, reactivation, and segmentation."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize lifecycle/CRM agent."""
        super().__init__(
            role="lifecycle-crm",
            name="Lifecycle / CRM Specialist",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get lifecycle/CRM domain expertise description."""
        return """Onboarding email sequences, reactivation campaigns, customer segmentation,
email automation, customer journey mapping, retention marketing, drip campaigns,
trigger-based messaging, personalization, email deliverability, A/B testing emails,
lifecycle stage definition, and customer engagement scoring."""
