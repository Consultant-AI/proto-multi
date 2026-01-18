"""
Bug Triage Agent.

Expertise in:
- Bug reproduction
- Priority assignment
- Issue routing
- Fix verification
- Bug tracking
- Root cause analysis
"""

from typing import Any

from .base_specialist import BaseSpecialist


class BugTriageAgent(BaseSpecialist):
    """Bug Triage specialist focused on reproducing, prioritizing, routing, and verifying fixes."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize bug triage agent."""
        super().__init__(
            role="bug-triage",
            name="Bug Triage Specialist",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get bug triage domain expertise description."""
        return """Bug reproduction, priority assignment, issue routing, fix verification,
bug tracking workflows, root cause analysis, severity classification, regression identification,
duplicate detection, bug report quality, environment reproduction, stakeholder communication,
fix validation testing, and bug metrics analysis."""
