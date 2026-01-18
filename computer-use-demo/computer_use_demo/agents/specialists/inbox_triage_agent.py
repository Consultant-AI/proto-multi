"""
Executive Inbox Triage Agent.

Expertise in:
- Email prioritization
- Request routing
- Urgency assessment
- Communication filtering
- Executive time protection
- Information distillation
"""

from typing import Any

from .base_specialist import BaseSpecialist


class InboxTriageAgent(BaseSpecialist):
    """Executive inbox triage specialist focused on prioritizing and routing communications."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize Inbox Triage agent."""
        super().__init__(
            role="inbox-triage",
            name="Inbox Triage",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get Inbox Triage domain expertise description."""
        return """Executive inbox prioritization and triage, email classification by urgency and importance,
request routing to appropriate team members, communication filtering, executive time protection,
information distillation and summarization, stakeholder communication management,
meeting request assessment, and ensuring critical items surface promptly."""
