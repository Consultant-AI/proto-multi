"""
Platform/API Product Agent.

Expertise in:
- API product management
- Platform strategy
- Developer experience
- API design
- Integration planning
- Platform ecosystem
"""

from typing import Any

from .base_specialist import BaseSpecialist


class PlatformAPIAgent(BaseSpecialist):
    """Platform/API product specialist focused on API and platform product management."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize Platform/API agent."""
        super().__init__(
            role="platform-api",
            name="Platform/API Product",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get Platform/API Product domain expertise description."""
        return """API product management, platform strategy development,
developer experience optimization, API design principles,
integration planning and partnerships, platform ecosystem development,
API versioning strategy, and developer adoption metrics."""
