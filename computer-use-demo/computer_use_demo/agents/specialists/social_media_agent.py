"""
Social Media Agent.

Expertise in:
- Social content creation
- Post scheduling
- Community engagement
- Platform strategy
- Social analytics
- Influencer coordination
"""

from typing import Any

from .base_specialist import BaseSpecialist


class SocialMediaAgent(BaseSpecialist):
    """Social Media specialist focused on posts, scheduling, and community engagement."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize social media agent."""
        super().__init__(
            role="social-media",
            name="Social Media Specialist",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get social media domain expertise description."""
        return """Social content creation, post scheduling, community engagement, platform strategy,
social analytics, influencer coordination, hashtag strategy, social listening,
community management, social customer service, viral content, social advertising,
user-generated content, and social media crisis management."""
