"""
Business Model Agent.

Expertise in:
- Business model design
- Revenue model innovation
- Value proposition
- Business model canvas
- Monetization strategy
- Model validation
"""

from typing import Any

from .base_specialist import BaseSpecialist


class BusinessModelAgent(BaseSpecialist):
    """Business model specialist focused on business model design and innovation."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize Business Model agent."""
        super().__init__(
            role="business-model",
            name="Business Model",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get Business Model domain expertise description."""
        return """Business model design and innovation, revenue model development,
value proposition refinement, business model canvas application,
monetization strategy, pricing model design,
business model validation, unit economics analysis,
and sustainable business model evolution."""
