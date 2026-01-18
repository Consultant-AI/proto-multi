"""
Frontend Developer Agent.

Expertise in:
- UI implementation
- Frontend performance
- State management
- Component architecture
- CSS/styling
- Browser compatibility
"""

from typing import Any

from .base_specialist import BaseSpecialist


class FrontendDeveloperAgent(BaseSpecialist):
    """Frontend Developer specialist focused on UI implementation, performance, and state management."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize frontend developer agent."""
        super().__init__(
            role="frontend-developer",
            name="Frontend Developer Specialist",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get frontend developer domain expertise description."""
        return """UI implementation, frontend performance optimization, state management (Redux, Context, Zustand),
component architecture, CSS/styling (CSS-in-JS, Tailwind, SCSS), browser compatibility,
React/Vue/Angular frameworks, responsive design, accessibility implementation,
frontend testing, bundle optimization, lazy loading, and frontend security."""
