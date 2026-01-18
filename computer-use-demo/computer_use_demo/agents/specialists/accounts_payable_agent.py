"""
Accounts Payable Agent.

Expertise in:
- Vendor bills
- Payment approvals
- Payment scheduling
- Expense management
- Bill processing
- Vendor payments
"""

from typing import Any

from .base_specialist import BaseSpecialist


class AccountsPayableAgent(BaseSpecialist):
    """Accounts Payable specialist focused on vendor bills, approvals, and payment scheduling."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize accounts payable agent."""
        super().__init__(
            role="accounts-payable",
            name="Accounts Payable Specialist",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get accounts payable domain expertise description."""
        return """Vendor bills processing, payment approvals, payment scheduling,
expense management, bill processing workflows, vendor payments, three-way matching,
payment terms management, early payment discounts, AP aging, vendor communication,
and payment documentation."""
