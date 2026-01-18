"""
Experimentation Agent.

Expertise in:
- A/B testing
- Experiment design
- Statistical analysis
- Feature flags
- Experiment tracking
- Results interpretation
"""

from typing import Any

from .base_specialist import BaseSpecialist


class ExperimentationAgent(BaseSpecialist):
    """Experimentation specialist focused on A/B tests for copy, flows, and processes."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize experimentation agent."""
        super().__init__(
            role="experimentation",
            name="Experimentation Specialist",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get experimentation domain expertise description."""
        return """A/B testing, experiment design, statistical analysis, feature flags,
experiment tracking, results interpretation, hypothesis formulation, sample size calculation,
multivariate testing, experiment prioritization, rollout strategies, experiment documentation,
statistical significance, effect size analysis, and experiment-driven decision making."""
