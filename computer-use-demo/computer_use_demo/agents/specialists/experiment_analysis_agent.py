"""
Experiment Analysis Agent.

Expertise in:
- Validity checks
- Effect size calculation
- Statistical decisions
- A/B test analysis
- Experimental design
- Results interpretation
"""

from typing import Any

from .base_specialist import BaseSpecialist


class ExperimentAnalysisAgent(BaseSpecialist):
    """Experiment Analysis specialist focused on validity checks, effect size, and decisions."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize experiment analysis agent."""
        super().__init__(
            role="experiment-analysis",
            name="Experiment Analysis Specialist",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get experiment analysis domain expertise description."""
        return """Validity checks, effect size calculation, statistical decision making, A/B test analysis,
experimental design review, results interpretation, statistical significance testing,
confidence intervals, power analysis, sample ratio mismatch detection, novelty effects,
Simpson's paradox detection, and causal inference."""
