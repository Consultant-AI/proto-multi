"""
Support Triage Agent.

Expertise in:
- Ticket classification
- Issue routing
- Priority assessment
- Initial diagnosis
- SLA management
- Queue management
"""

from typing import Any

from .base_specialist import BaseSpecialist


class SupportTriageAgent(BaseSpecialist):
    """Support Triage specialist focused on classifying tickets, routing, and prioritizing."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize support triage agent."""
        super().__init__(
            role="support-triage",
            name="Support Triage Specialist",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get support triage domain expertise description."""
        return """Ticket classification, issue routing, priority assessment, initial diagnosis,
SLA management, queue management, severity determination, escalation identification,
duplicate detection, customer sentiment analysis, first response handling,
ticket tagging, and triage automation."""
