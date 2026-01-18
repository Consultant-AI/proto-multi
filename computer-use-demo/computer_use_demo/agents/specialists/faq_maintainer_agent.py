"""
FAQ Maintainer Agent.

Expertise in:
- FAQ management
- Question curation
- Answer accuracy
- Common query identification
- Self-service content
- FAQ analytics
"""

from typing import Any

from .base_specialist import BaseSpecialist


class FAQMaintainerAgent(BaseSpecialist):
    """FAQ maintainer specialist focused on managing frequently asked questions."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize FAQ Maintainer agent."""
        super().__init__(
            role="faq-maintainer",
            name="FAQ Maintainer",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get FAQ Maintainer domain expertise description."""
        return """FAQ management and maintenance, question curation and categorization,
answer accuracy verification, common query identification from support data,
self-service content optimization, FAQ analytics and usage tracking,
answer freshness management, and FAQ gap identification."""
