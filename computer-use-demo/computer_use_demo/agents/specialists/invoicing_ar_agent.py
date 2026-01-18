"""
Invoicing/AR Agent.

Expertise in:
- Invoice generation
- Collections
- Payment follow-ups
- Accounts receivable
- Billing cycles
- Payment tracking
"""

from typing import Any

from .base_specialist import BaseSpecialist


class InvoicingARAgent(BaseSpecialist):
    """Invoicing/AR specialist focused on billing, collections, and payment follow-ups."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize invoicing/AR agent."""
        super().__init__(
            role="invoicing-ar",
            name="Invoicing / AR Specialist",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get invoicing/AR domain expertise description."""
        return """Invoice generation, collections management, payment follow-ups,
accounts receivable management, billing cycles, payment tracking, aging reports,
customer payment terms, dunning processes, payment reminders, credit memos,
and cash application."""
