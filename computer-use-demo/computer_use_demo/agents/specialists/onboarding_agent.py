"""
Onboarding Agent.

Expertise in:
- Setup steps
- Training plans
- Onboarding checklists
- Time to value
- Implementation guides
- Go-live support
"""

from typing import Any

from .base_specialist import BaseSpecialist


class OnboardingAgent(BaseSpecialist):
    """Onboarding specialist focused on setup steps, training plans, and checklists."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize onboarding agent."""
        super().__init__(
            role="onboarding",
            name="Onboarding Specialist",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get onboarding domain expertise description."""
        return """Setup steps, training plans, onboarding checklists, time to value optimization,
implementation guides, go-live support, customer kickoff, success milestones,
adoption tracking, onboarding automation, user provisioning, data migration support,
configuration assistance, and early success metrics."""
