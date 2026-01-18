"""
CLO Agent.

Expertise in:
- Legal strategy
- Corporate governance
- Compliance oversight
- Risk management
- Contract strategy
- Legal leadership
"""

from typing import Any

from .base_specialist import BaseSpecialist


class CLOAgent(BaseSpecialist):
    """CLO specialist focused on legal strategy and compliance."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize CLO agent."""
        super().__init__(
            role="clo",
            name="CLO",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get CLO domain expertise description."""
        return """Legal strategy, corporate governance, compliance oversight, risk management,
contract strategy, legal leadership, regulatory affairs, intellectual property strategy,
litigation management, corporate transactions, legal operations,
and cross-functional legal coordination."""
