"""
Support Resolution Agent.

Expertise in:
- Answer drafting
- Troubleshooting
- Issue escalation
- Resolution verification
- Customer communication
- Technical support
"""

from typing import Any

from .base_specialist import BaseSpecialist


class SupportResolutionAgent(BaseSpecialist):
    """Support Resolution specialist focused on drafting answers, troubleshooting, and escalation."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize support resolution agent."""
        super().__init__(
            role="support-resolution",
            name="Support Resolution Specialist",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get support resolution domain expertise description."""
        return """Answer drafting, troubleshooting, issue escalation, resolution verification,
customer communication, technical support, root cause identification, workaround provision,
step-by-step guidance, screen sharing support, ticket documentation, resolution time optimization,
customer satisfaction, and issue prevention."""
