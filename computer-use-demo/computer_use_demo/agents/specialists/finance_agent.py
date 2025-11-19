"""
Finance Specialist Agent.

Expertise in:
- Financial planning and analysis
- Budgeting and forecasting
- Revenue recognition
- Financial reporting
- Accounting operations
- Financial metrics
"""

from typing import Any

from .base_specialist import BaseSpecialist


class FinanceAgent(BaseSpecialist):
    """Finance specialist focused on financial planning and operations."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None):
        """Initialize finance agent."""
        super().__init__(
            role="finance",
            name="Finance Specialist",
            session_id=session_id,
            tools=tools,
        )

    def get_domain_expertise(self) -> str:
        """Get finance domain expertise description."""
        return """Financial planning and analysis (FP&A), budgeting and forecasting, revenue recognition,
financial reporting (P&L, balance sheet, cash flow), accounting operations, financial metrics (ARR, MRR, CAC, LTV),
fundraising and investor relations, financial modeling, tax planning, audit compliance, expense management,
and SaaS financial metrics."""
