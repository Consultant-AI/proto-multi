"""
Experiment Design Agent.

Expertise in:
- Experiment methodology
- Statistical design
- Sample size calculation
- Test duration planning
- Metric selection
- Bias prevention
"""

from typing import Any

from .base_specialist import BaseSpecialist


class ExperimentDesignAgent(BaseSpecialist):
    """Experiment design specialist focused on rigorous experiment methodology."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize Experiment Design agent."""
        super().__init__(
            role="experiment-design",
            name="Experiment Design",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get Experiment Design domain expertise description."""
        return """Experiment methodology and design, statistical test selection,
sample size calculation and power analysis, test duration planning,
primary and secondary metric selection, bias prevention strategies,
randomization design, and experiment validity assurance."""
