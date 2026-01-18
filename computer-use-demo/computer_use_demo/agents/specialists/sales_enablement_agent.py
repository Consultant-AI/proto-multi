"""
Sales Enablement Agent.

Expertise in:
- Battlecards
- Pitch decks
- Sales training
- Competitive intel
- Sales playbooks
- Objection handling guides
"""

from typing import Any

from .base_specialist import BaseSpecialist


class SalesEnablementAgent(BaseSpecialist):
    """Sales Enablement specialist focused on battlecards, pitch decks, and training."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize sales enablement agent."""
        super().__init__(
            role="sales-enablement",
            name="Sales Enablement Specialist",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get sales enablement domain expertise description."""
        return """Battlecards, pitch decks, sales training content, competitive intelligence,
sales playbooks, objection handling guides, product training, demo scripts,
case studies, ROI calculators, sales certification programs, onboarding materials,
content management, and enablement metrics."""
