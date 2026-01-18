"""
Product Discovery Agent.

Expertise in:
- Problem selection
- Opportunity sizing
- Jobs to be done (JTBD)
- Market validation
- Feature prioritization
- Discovery frameworks
"""

from typing import Any

from .base_specialist import BaseSpecialist


class ProductDiscoveryAgent(BaseSpecialist):
    """Product Discovery specialist focused on problem selection, opportunity sizing, and JTBD."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize product discovery agent."""
        super().__init__(
            role="product-discovery",
            name="Product Discovery Specialist",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get product discovery domain expertise description."""
        return """Problem selection, opportunity sizing, jobs to be done (JTBD), market validation,
feature prioritization, discovery frameworks, customer development, problem-solution fit,
opportunity scoring, discovery sprints, assumption testing, rapid prototyping,
market opportunity analysis, and customer pain point identification."""
