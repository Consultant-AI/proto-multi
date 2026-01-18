"""
Churn Prevention Agent.

Expertise in:
- Risk detection
- Intervention triggers
- Retention strategies
- Health scoring
- Win-back campaigns
- Early warning signals
"""

from typing import Any

from .base_specialist import BaseSpecialist


class ChurnPreventionAgent(BaseSpecialist):
    """Churn Prevention specialist focused on detecting risk and triggering interventions."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize churn prevention agent."""
        super().__init__(
            role="churn-prevention",
            name="Churn Prevention Specialist",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get churn prevention domain expertise description."""
        return """Risk detection, intervention triggers, retention strategies, health scoring,
win-back campaigns, early warning signals, usage decline detection, engagement tracking,
save offers, customer outreach, churn prediction models, retention playbooks,
executive escalation, and post-churn analysis."""
