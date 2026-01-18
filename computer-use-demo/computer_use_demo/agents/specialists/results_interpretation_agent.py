"""
Results Interpretation Agent.

Expertise in:
- Statistical analysis
- Result interpretation
- Significance testing
- Effect size analysis
- Confidence intervals
- Recommendation synthesis
"""

from typing import Any

from .base_specialist import BaseSpecialist


class ResultsInterpretationAgent(BaseSpecialist):
    """Results interpretation specialist focused on analyzing experiment outcomes."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize Results Interpretation agent."""
        super().__init__(
            role="results-interpretation",
            name="Results Interpretation",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get Results Interpretation domain expertise description."""
        return """Statistical analysis of experiment results, result interpretation and narrative,
significance testing and p-value analysis, effect size calculation,
confidence interval interpretation, recommendation synthesis from data,
segment analysis, and actionable insight generation."""
