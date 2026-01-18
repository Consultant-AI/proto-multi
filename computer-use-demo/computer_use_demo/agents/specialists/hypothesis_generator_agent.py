"""
Hypothesis Generator Agent.

Expertise in:
- Hypothesis formulation
- Testable predictions
- Assumption identification
- Research questions
- Scientific method
- Hypothesis prioritization
"""

from typing import Any

from .base_specialist import BaseSpecialist


class HypothesisGeneratorAgent(BaseSpecialist):
    """Hypothesis generator specialist focused on formulating testable hypotheses."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize Hypothesis Generator agent."""
        super().__init__(
            role="hypothesis-generator",
            name="Hypothesis Generator",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get Hypothesis Generator domain expertise description."""
        return """Hypothesis formulation and generation, testable prediction development,
assumption identification and validation, research question framing,
scientific method application, hypothesis prioritization,
null and alternative hypothesis design, and measurable outcome definition."""
