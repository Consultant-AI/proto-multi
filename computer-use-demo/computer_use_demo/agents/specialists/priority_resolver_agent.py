"""
Priority Conflict Resolver Agent.

Expertise in:
- Priority arbitration
- Resource conflict resolution
- Trade-off analysis
- Stakeholder alignment
- Decision escalation
- Competing demand management
"""

from typing import Any

from .base_specialist import BaseSpecialist


class PriorityResolverAgent(BaseSpecialist):
    """Priority resolver specialist focused on resolving competing priorities and conflicts."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize Priority Resolver agent."""
        super().__init__(
            role="priority-resolver",
            name="Priority Resolver",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get Priority Resolver domain expertise description."""
        return """Priority conflict resolution and arbitration, resource allocation conflicts,
trade-off analysis and recommendation, stakeholder alignment facilitation,
decision escalation management, competing demand assessment,
cross-team priority negotiation, strategic alignment verification,
and ensuring organizational focus on highest-impact work."""
