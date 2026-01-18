"""
Incident Commander Agent.

Expertise in:
- Incident management
- Crisis coordination
- Response leadership
- Communication management
- Escalation handling
- Incident resolution
"""

from typing import Any

from .base_specialist import BaseSpecialist


class IncidentCommanderAgent(BaseSpecialist):
    """Incident commander specialist focused on leading incident response and resolution."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize Incident Commander agent."""
        super().__init__(
            role="incident-commander",
            name="Incident Commander",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get Incident Commander domain expertise description."""
        return """Incident command and leadership, crisis coordination,
response team management, stakeholder communication during incidents,
escalation handling and decision making, incident resolution coordination,
resource mobilization, timeline management, and incident documentation."""
