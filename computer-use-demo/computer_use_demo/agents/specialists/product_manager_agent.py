"""
Product Manager Specialist Agent.

Expertise in:
- Product strategy and roadmapping
- Requirements gathering
- User story creation
- Feature prioritization
- Stakeholder management
- Product analytics
"""

from typing import Any

from .base_specialist import BaseSpecialist


class ProductManagerAgent(BaseSpecialist):
    """Product Manager specialist focused on product strategy and execution."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None):
        """Initialize product manager agent."""
        super().__init__(
            role="product-manager",
            name="Product Manager Specialist",
            session_id=session_id,
            tools=tools,
        )

    def get_domain_expertise(self) -> str:
        """Get product management domain expertise description."""
        return """Product strategy, product roadmapping, requirements gathering and analysis,
user story creation, feature prioritization (RICE, MoSCoW), stakeholder management,
product analytics, A/B testing, user research, competitive analysis, go-to-market strategy,
product lifecycle management, and agile/scrum methodologies."""
