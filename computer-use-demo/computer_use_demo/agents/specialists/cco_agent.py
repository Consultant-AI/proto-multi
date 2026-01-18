"""
CCO Agent.

Expertise in:
- Customer success strategy
- Customer experience
- Retention strategy
- Customer satisfaction
- Support excellence
- Customer leadership
"""

from typing import Any

from .base_specialist import BaseSpecialist


class CCOAgent(BaseSpecialist):
    """CCO specialist focused on customer success and experience."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize CCO agent."""
        super().__init__(
            role="cco",
            name="CCO",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get CCO domain expertise description."""
        return """Customer success strategy, customer experience, retention strategy,
customer satisfaction, support excellence, customer leadership, NPS improvement,
customer journey optimization, churn reduction, customer health scoring,
voice of customer programs, and cross-functional customer coordination."""
