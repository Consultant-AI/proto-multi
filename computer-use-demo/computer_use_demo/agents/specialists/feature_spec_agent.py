"""
Feature Spec Writer Agent.

Expertise in:
- Feature specifications
- Requirements writing
- Acceptance criteria
- User story creation
- Technical requirements
- Specification review
"""

from typing import Any

from .base_specialist import BaseSpecialist


class FeatureSpecAgent(BaseSpecialist):
    """Feature spec writer specialist focused on writing detailed feature specifications."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize Feature Spec agent."""
        super().__init__(
            role="feature-spec",
            name="Feature Spec Writer",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get Feature Spec Writer domain expertise description."""
        return """Feature specification writing, requirements documentation,
acceptance criteria definition, user story creation,
technical requirements translation, edge case identification,
specification review and feedback, and scope clarification."""
