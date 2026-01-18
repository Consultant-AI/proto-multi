"""
Community Agent.

Expertise in:
- Forum management
- Community moderation
- Ambassador programs
- User engagement
- Community events
- Peer support
"""

from typing import Any

from .base_specialist import BaseSpecialist


class CommunityAgent(BaseSpecialist):
    """Community specialist focused on forums, moderation, and ambassador programs."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize community agent."""
        super().__init__(
            role="community",
            name="Community Specialist",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get community domain expertise description."""
        return """Forum management, community moderation, ambassador programs, user engagement,
community events, peer support facilitation, community guidelines, user recognition,
community metrics, discussion facilitation, community growth, conflict resolution,
power user cultivation, and community platform management."""
