"""
Risk Agent.

Expertise in:
- Enterprise risk register
- Mitigation plans
- Risk assessment
- Risk monitoring
- Business continuity
- Risk reporting
"""

from typing import Any

from .base_specialist import BaseSpecialist


class RiskAgent(BaseSpecialist):
    """Risk specialist focused on enterprise risk register and mitigation plans."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize risk agent."""
        super().__init__(
            role="risk",
            name="Risk Specialist",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get risk domain expertise description."""
        return """Enterprise risk register, mitigation plans, risk assessment, risk monitoring,
business continuity planning, risk reporting, risk scoring, risk ownership,
control effectiveness, key risk indicators, risk appetite, disaster recovery,
and risk communication."""
