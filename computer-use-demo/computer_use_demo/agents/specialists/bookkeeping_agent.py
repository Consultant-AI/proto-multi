"""
Bookkeeping Agent.

Expertise in:
- Reconciliations
- Transaction categorization
- Month-end close
- Account maintenance
- Financial records
- Ledger management
"""

from typing import Any

from .base_specialist import BaseSpecialist


class BookkeepingAgent(BaseSpecialist):
    """Bookkeeping specialist focused on reconciliations, categorization, and close tasks."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize bookkeeping agent."""
        super().__init__(
            role="bookkeeping",
            name="Bookkeeping Specialist",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get bookkeeping domain expertise description."""
        return """Reconciliations, transaction categorization, month-end close tasks,
account maintenance, financial records, ledger management, bank reconciliation,
credit card reconciliation, journal entries, chart of accounts maintenance,
accruals, and financial data accuracy."""
