"""
Policy & Guardrails Agent.

Expertise in:
- Permission management
- Approval workflows
- Policy enforcement
- Access control policies
- Operational boundaries
- Compliance guardrails
"""

from typing import Any

from .base_specialist import BaseSpecialist


class PolicyGuardrailsAgent(BaseSpecialist):
    """Policy & Guardrails specialist focused on permissions, approvals, and operational boundaries."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize policy guardrails agent."""
        super().__init__(
            role="policy-guardrails",
            name="Policy & Guardrails Specialist",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get policy & guardrails domain expertise description."""
        return """Permission management, approval workflows, policy enforcement, access control policies,
operational boundaries, compliance guardrails, what actions are allowed, authorization rules,
policy documentation, exception handling, escalation procedures, governance frameworks,
policy auditing, and boundary enforcement."""
