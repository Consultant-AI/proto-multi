"""
Incident Response Agent.

Expertise in:
- Incident runbooks
- Communications
- Postmortems
- Incident triage
- Escalation procedures
- Recovery coordination
"""

from typing import Any

from .base_specialist import BaseSpecialist


class IncidentResponseAgent(BaseSpecialist):
    """Incident Response specialist focused on runbooks, comms, and postmortems."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize incident response agent."""
        super().__init__(
            role="incident-response",
            name="Incident Response Specialist",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get incident response domain expertise description."""
        return """Incident runbooks, incident communications, postmortems, incident triage,
escalation procedures, recovery coordination, incident commander role,
status page updates, stakeholder communication, root cause analysis,
incident timeline documentation, and lessons learned."""
