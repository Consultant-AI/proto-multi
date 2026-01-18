"""
Decision Memo Writer Agent.

Expertise in:
- Decision documentation
- Options analysis
- Recommendation framing
- Executive briefings
- Strategic communication
- Risk assessment presentation
"""

from typing import Any

from .base_specialist import BaseSpecialist


class DecisionMemoAgent(BaseSpecialist):
    """Decision memo writer specialist focused on structuring decisions for executive review."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize Decision Memo agent."""
        super().__init__(
            role="decision-memo",
            name="Decision Memo Writer",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get Decision Memo Writer domain expertise description."""
        return """Decision documentation and memo writing, options analysis and comparison,
recommendation framing with clear rationale, executive briefing preparation,
risk-benefit assessment presentation, stakeholder impact analysis,
decision tree construction, scenario modeling for decisions,
and structured argumentation for leadership review."""
