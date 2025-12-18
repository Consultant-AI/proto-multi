"""
Sales Specialist Agent.

Expertise in:
- Sales strategy
- Lead qualification
- Sales presentations
- Deal negotiation
- Pipeline management
- Sales enablement
"""

from typing import Any

from .base_specialist import BaseSpecialist


class SalesAgent(BaseSpecialist):
    """Sales specialist focused on revenue generation and deal closing."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize sales agent."""
        super().__init__(
            role="sales",
            name="Sales Specialist",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get sales domain expertise description."""
        return """Sales strategy and planning, lead qualification (BANT, MEDDIC), sales presentations and demos,
deal negotiation and closing, pipeline management and forecasting, sales enablement and training,
account-based selling, value proposition development, pricing and proposals, CRM management (Salesforce, HubSpot),
sales metrics and reporting, competitive positioning, and relationship building."""
