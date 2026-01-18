"""
Scenario Planning Agent.

Expertise in:
- Future scenario modeling
- Contingency planning
- Risk scenario analysis
- Strategic alternatives
- What-if analysis
- Planning under uncertainty
"""

from typing import Any

from .base_specialist import BaseSpecialist


class ScenarioPlanningAgent(BaseSpecialist):
    """Scenario planning specialist focused on future scenario modeling and contingencies."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize Scenario Planning agent."""
        super().__init__(
            role="scenario-planning",
            name="Scenario Planning",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get Scenario Planning domain expertise description."""
        return """Future scenario modeling and development, contingency planning,
risk scenario analysis, strategic alternative evaluation,
what-if analysis and simulation, planning under uncertainty,
black swan event preparation, scenario probability assessment,
and adaptive strategy development."""
