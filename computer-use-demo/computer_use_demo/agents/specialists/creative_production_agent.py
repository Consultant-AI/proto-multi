"""
Creative Production Agent.

Expertise in:
- Graphics creation
- Video scripts
- Landing page assets
- Creative briefs
- Asset production
- Design coordination
"""

from typing import Any

from .base_specialist import BaseSpecialist


class CreativeProductionAgent(BaseSpecialist):
    """Creative Production specialist focused on graphics, video scripts, and landing assets."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize creative production agent."""
        super().__init__(
            role="creative-production",
            name="Creative Production Specialist",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get creative production domain expertise description."""
        return """Graphics creation, video scripts, landing page assets, creative briefs,
asset production workflow, design coordination, ad creative, social graphics,
email design, presentation design, brand asset creation, creative testing,
asset versioning, and production timeline management."""
