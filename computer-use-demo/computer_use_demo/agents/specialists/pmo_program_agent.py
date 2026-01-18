"""
PMO / Program Agent.

Expertise in:
- Program management
- Roadmap planning
- Dependency tracking
- Milestone management
- Risk tracking
- Portfolio coordination
"""

from typing import Any

from .base_specialist import BaseSpecialist


class PMOProgramAgent(BaseSpecialist):
    """PMO/Program specialist focused on program management and roadmap coordination."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize PMO program agent."""
        super().__init__(
            role="pmo-program",
            name="PMO / Program Specialist",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get PMO/program domain expertise description."""
        return """Program management, roadmap planning, dependency tracking, milestone management,
risk tracking, portfolio coordination, resource planning, cross-project alignment,
deliverable tracking, program governance, stakeholder reporting, timeline management,
critical path analysis, and program-level decision making."""
