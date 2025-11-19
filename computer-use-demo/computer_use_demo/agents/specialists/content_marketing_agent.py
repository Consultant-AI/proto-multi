"""
Content Marketing Specialist Agent.

Expertise in:
- Content strategy
- Blog and article writing
- SEO content optimization
- Social media content
- Video and multimedia
- Content distribution
"""

from typing import Any

from .base_specialist import BaseSpecialist


class ContentMarketingAgent(BaseSpecialist):
    """Content Marketing specialist focused on content creation and distribution."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None):
        """Initialize content marketing agent."""
        super().__init__(
            role="content-marketing",
            name="Content Marketing Specialist",
            session_id=session_id,
            tools=tools,
        )

    def get_domain_expertise(self) -> str:
        """Get content marketing domain expertise description."""
        return """Content strategy and planning, blog and article writing, SEO content optimization,
social media content creation, video and multimedia content, content distribution and promotion,
editorial calendar management, content performance analytics, thought leadership, case studies and whitepapers,
copywriting, and content marketing ROI measurement."""
