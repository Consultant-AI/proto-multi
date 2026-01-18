"""
Accessibility Agent.

Expertise in:
- WCAG compliance
- Accessibility testing
- Screen reader support
- Keyboard navigation
- Color contrast
- Assistive technology
"""

from typing import Any

from .base_specialist import BaseSpecialist


class AccessibilityAgent(BaseSpecialist):
    """Accessibility specialist focused on WCAG checks, fixes, and testing."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize accessibility agent."""
        super().__init__(
            role="accessibility",
            name="Accessibility Specialist",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get accessibility domain expertise description."""
        return """WCAG compliance, accessibility testing, screen reader support, keyboard navigation,
color contrast analysis, assistive technology compatibility, ARIA attributes,
semantic HTML, focus management, accessibility auditing, remediation strategies,
inclusive design, accessibility documentation, and accessibility best practices."""
