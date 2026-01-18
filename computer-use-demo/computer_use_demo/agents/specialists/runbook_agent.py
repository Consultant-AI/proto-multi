"""
Runbook Agent.

Expertise in:
- Runbook creation
- Operational procedures
- Process documentation
- Automation scripts
- Standard operating procedures
- Playbook management
"""

from typing import Any

from .base_specialist import BaseSpecialist


class RunbookAgent(BaseSpecialist):
    """Runbook specialist focused on creating and maintaining operational runbooks."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize Runbook agent."""
        super().__init__(
            role="runbook",
            name="Runbook",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get Runbook domain expertise description."""
        return """Runbook creation and maintenance, operational procedure documentation,
step-by-step process guides, automation script development,
standard operating procedure design, playbook management,
troubleshooting guides, and operational knowledge capture."""
