"""
SRE (Site Reliability Engineering) Agent.

Expertise in:
- Reliability targets
- SLOs/SLIs/SLAs
- Incident response
- Postmortems
- Capacity planning
- Error budgets
"""

from typing import Any

from .base_specialist import BaseSpecialist


class SREAgent(BaseSpecialist):
    """SRE specialist focused on reliability targets, SLOs, incident response, and postmortems."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize SRE agent."""
        super().__init__(
            role="sre",
            name="SRE Specialist",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get SRE domain expertise description."""
        return """Reliability targets, SLOs/SLIs/SLAs, incident response, postmortems,
capacity planning, error budgets, toil reduction, on-call management, chaos engineering,
runbook creation, service level management, production readiness, reliability metrics,
incident management, and blameless culture."""
