"""
Contract Agent.

Expertise in:
- Contract drafting
- Redlining
- MSAs, DPAs, SOWs, NDAs
- Contract review
- Terms negotiation
- Contract management
"""

from typing import Any

from .base_specialist import BaseSpecialist


class ContractAgent(BaseSpecialist):
    """Contract specialist focused on drafts/redlines for MSAs, DPAs, SOWs, and NDAs."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize contract agent."""
        super().__init__(
            role="contract",
            name="Contract Specialist",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get contract domain expertise description."""
        return """Contract drafting, redlining, MSAs, DPAs, SOWs, NDAs, contract review,
terms negotiation, contract management, amendment creation, contract templates,
risk identification in contracts, liability clauses, indemnification terms,
and contract lifecycle management."""
