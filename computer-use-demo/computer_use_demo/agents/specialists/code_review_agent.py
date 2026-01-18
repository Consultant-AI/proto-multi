"""
Code Review Agent.

Expertise in:
- Code correctness
- Style consistency
- Security review
- Maintainability
- Performance review
- Best practices
"""

from typing import Any

from .base_specialist import BaseSpecialist


class CodeReviewAgent(BaseSpecialist):
    """Code Review specialist focused on correctness, style, security, and maintainability."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize code review agent."""
        super().__init__(
            role="code-review",
            name="Code Review Specialist",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get code review domain expertise description."""
        return """Code correctness verification, style consistency, security review, maintainability assessment,
performance review, best practices enforcement, code quality metrics, design pattern review,
technical debt identification, PR review workflows, constructive feedback, code standards,
refactoring suggestions, and documentation review."""
