"""
Tax Agent.

Expertise in:
- Tax filings preparation
- Compliance checklists
- Tax regulations
- Sales tax
- Tax documentation
- Tax planning
"""

from typing import Any

from .base_specialist import BaseSpecialist


class TaxAgent(BaseSpecialist):
    """Tax specialist focused on filings prep and compliance checklists (with human sign-off)."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize tax agent."""
        super().__init__(
            role="tax",
            name="Tax Specialist",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get tax domain expertise description."""
        return """Tax filings preparation, compliance checklists, tax regulations,
sales tax management, tax documentation, tax planning support, nexus analysis,
tax exemptions, 1099 preparation, tax calendar management, audit preparation,
and tax jurisdiction tracking. Note: Human sign-off required for actual filings."""
