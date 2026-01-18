"""
Voice of Customer Agent.

Expertise in:
- Feedback mining
- Theme identification
- Product requests
- NPS analysis
- Customer insights
- Feedback synthesis
"""

from typing import Any

from .base_specialist import BaseSpecialist


class VoiceOfCustomerAgent(BaseSpecialist):
    """Voice of Customer specialist focused on feedback mining, themes, and product requests."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize voice of customer agent."""
        super().__init__(
            role="voice-of-customer",
            name="Voice of Customer Specialist",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get voice of customer domain expertise description."""
        return """Feedback mining, theme identification, product requests aggregation,
NPS analysis, customer insights, feedback synthesis, sentiment analysis,
feature request prioritization, customer advisory boards, feedback loops,
survey design, verbatim analysis, and customer journey feedback."""
