"""
Localization Manager Agent.

Expertise in:
- Localization strategy
- Translation management
- i18n coordination
- Cultural adaptation
- Language coverage
- Localization QA
"""

from typing import Any

from .base_specialist import BaseSpecialist


class LocalizationAgent(BaseSpecialist):
    """Localization manager specialist focused on product localization."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize Localization agent."""
        super().__init__(
            role="localization",
            name="Localization Manager",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get Localization Manager domain expertise description."""
        return """Localization strategy and planning, translation management,
internationalization (i18n) coordination, cultural adaptation,
language coverage prioritization, localization quality assurance,
string extraction and management, and regional compliance."""
