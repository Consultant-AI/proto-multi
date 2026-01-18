"""
Compensation & Benefits Agent.

Expertise in:
- Benchmarking
- Offer creation
- Payroll coordination
- Benefits administration
- Compensation planning
- Equity programs
"""

from typing import Any

from .base_specialist import BaseSpecialist


class CompensationBenefitsAgent(BaseSpecialist):
    """Comp/Benefits specialist focused on benchmarking, offers, and payroll coordination."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize compensation & benefits agent."""
        super().__init__(
            role="compensation-benefits",
            name="Compensation & Benefits Specialist",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get compensation & benefits domain expertise description."""
        return """Compensation benchmarking, offer creation, payroll coordination,
benefits administration, compensation planning, equity programs, salary bands,
total rewards, benefits enrollment, compensation equity analysis, bonus programs,
and benefits vendor management."""
