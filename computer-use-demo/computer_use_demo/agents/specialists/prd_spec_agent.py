"""
PRD/Spec Agent.

Expertise in:
- Requirements writing
- Acceptance criteria
- Edge case documentation
- User story creation
- Technical specifications
- Feature documentation
"""

from typing import Any

from .base_specialist import BaseSpecialist


class PRDSpecAgent(BaseSpecialist):
    """PRD/Spec specialist focused on writing requirements, acceptance criteria, and edge cases."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize PRD/spec agent."""
        super().__init__(
            role="prd-spec",
            name="PRD / Spec Specialist",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get PRD/spec domain expertise description."""
        return """Requirements writing, acceptance criteria definition, edge case documentation,
user story creation, technical specifications, feature documentation, PRD templates,
requirements prioritization, scope definition, success metrics, functional requirements,
non-functional requirements, dependency mapping, and requirements traceability."""
