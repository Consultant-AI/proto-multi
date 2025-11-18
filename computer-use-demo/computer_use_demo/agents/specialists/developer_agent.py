"""
Development Specialist Agent.

Expertise in:
- Software development
- Architecture design
- Code implementation
- Testing and debugging
- Performance optimization
- Technical documentation
"""

from typing import Any

from .base_specialist import BaseSpecialist


class DeveloperAgent(BaseSpecialist):
    """Development specialist focused on software engineering."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None):
        """Initialize developer agent."""
        super().__init__(
            role="development",
            name="Development Specialist",
            session_id=session_id,
            tools=tools,
        )

    def get_domain_expertise(self) -> str:
        """Get development domain expertise description."""
        return """Software engineering, system architecture, full-stack development (frontend and backend),
database design, API development, code quality and testing, performance optimization,
security best practices, DevOps, CI/CD, technical documentation, and code review."""
