"""
Content Design Agent.

Expertise in:
- Microcopy writing
- Onboarding text
- Error messages
- UI text
- Voice and tone
- Content strategy
"""

from typing import Any

from .base_specialist import BaseSpecialist


class ContentDesignAgent(BaseSpecialist):
    """Content Design specialist focused on microcopy, onboarding text, and error messages."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize content design agent."""
        super().__init__(
            role="content-design",
            name="Content Design Specialist",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get content design domain expertise description."""
        return """Microcopy writing, onboarding text, error messages, UI text,
voice and tone guidelines, content strategy, button labels, form instructions,
help text, tooltips, empty states, confirmation messages, notification copy,
accessibility in content, localization-ready content, and content consistency."""
