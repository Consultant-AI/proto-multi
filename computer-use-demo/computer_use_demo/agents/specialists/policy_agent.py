"""
Policy Agent.

Expertise in:
- Terms of service
- Privacy policies
- Internal policies
- Policy drafting
- Policy updates
- Compliance requirements
"""

from typing import Any

from .base_specialist import BaseSpecialist


class PolicyAgent(BaseSpecialist):
    """Policy specialist focused on ToS, privacy policy, and internal policies."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize policy agent."""
        super().__init__(
            role="policy",
            name="Policy Specialist",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get policy domain expertise description."""
        return """Terms of service, privacy policies, internal policies, policy drafting,
policy updates, compliance requirements, acceptable use policies, cookie policies,
employee handbooks, code of conduct, policy communication, policy training,
and policy version control."""
