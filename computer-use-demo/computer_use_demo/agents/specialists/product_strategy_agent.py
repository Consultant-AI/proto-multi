"""
Product Strategy Specialist Agent.

Expertise in:
- Product vision and strategy
- Market research
- Competitive analysis
- Product positioning
- Go-to-market planning
- Product innovation
"""

from typing import Any

from .base_specialist import BaseSpecialist


class ProductStrategyAgent(BaseSpecialist):
    """Product Strategy specialist focused on long-term product vision and market strategy."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize product strategy agent."""
        super().__init__(
            role="product-strategy",
            name="Product Strategy Specialist",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get product strategy domain expertise description."""
        return """Product vision and strategy development, market research and analysis, competitive analysis
and positioning, product-market fit, go-to-market planning and execution, product innovation and differentiation,
pricing strategy, product portfolio management, strategic partnerships, market segmentation,
and long-term product planning."""
