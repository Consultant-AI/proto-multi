"""
UI/Visual Design Agent.

Expertise in:
- Component design
- Brand consistency
- Layout design
- Visual hierarchy
- Design systems
- Color and typography
"""

from typing import Any

from .base_specialist import BaseSpecialist


class UIVisualDesignAgent(BaseSpecialist):
    """UI/Visual Design specialist focused on components, brand consistency, and layout."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize UI/visual design agent."""
        super().__init__(
            role="ui-visual-design",
            name="UI / Visual Design Specialist",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get UI/visual design domain expertise description."""
        return """Component design, brand consistency, layout design, visual hierarchy,
design systems, color theory, typography, iconography, spacing and grid systems,
responsive design, visual polish, design tokens, style guides, UI patterns,
motion design, and pixel-perfect implementation."""
