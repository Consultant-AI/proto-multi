"""
Procurement Agent.

Expertise in:
- Purchase requests
- Vendor comparisons
- Approval workflows
- Cost negotiation
- Contract terms
- Purchasing policies
"""

from typing import Any

from .base_specialist import BaseSpecialist


class ProcurementAgent(BaseSpecialist):
    """Procurement specialist focused on purchase requests, comparisons, and approvals."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize procurement agent."""
        super().__init__(
            role="procurement",
            name="Procurement Specialist",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get procurement domain expertise description."""
        return """Purchase requests, vendor comparisons, approval workflows, cost negotiation,
contract terms review, purchasing policies, RFP/RFQ processes, budget alignment,
procurement compliance, order tracking, spend analysis, and supplier evaluation."""
