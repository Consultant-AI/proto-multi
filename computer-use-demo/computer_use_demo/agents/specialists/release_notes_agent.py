"""
Release Notes Writer Agent.

Expertise in:
- Release documentation
- Changelog writing
- Feature announcements
- User communication
- Version documentation
- Migration guides
"""

from typing import Any

from .base_specialist import BaseSpecialist


class ReleaseNotesAgent(BaseSpecialist):
    """Release notes writer specialist focused on documenting releases."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize Release Notes agent."""
        super().__init__(
            role="release-notes",
            name="Release Notes Writer",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get Release Notes Writer domain expertise description."""
        return """Release notes and changelog writing, feature announcement drafting,
user-facing communication, version documentation,
breaking change documentation, migration guide creation,
release summary compilation, and multi-audience release messaging."""
