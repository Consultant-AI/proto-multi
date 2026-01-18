"""
Strategic Initiative Agent.

Expertise in:
- Initiative planning
- Strategic projects
- Cross-functional programs
- Initiative tracking
- Strategic execution
- Program governance
"""

from typing import Any

from .base_specialist import BaseSpecialist


class StrategicInitiativeAgent(BaseSpecialist):
    """Strategic initiative specialist focused on planning and executing strategic programs."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize Strategic Initiative agent."""
        super().__init__(
            role="strategic-initiative",
            name="Strategic Initiative",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get Strategic Initiative domain expertise description."""
        return """Strategic initiative planning and execution, cross-functional program design,
initiative prioritization, strategic project governance,
milestone tracking and reporting, initiative resource coordination,
stakeholder alignment, success criteria definition,
and strategic program delivery."""
