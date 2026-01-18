"""
Anomaly Explanation Agent.

Expertise in:
- Anomaly detection
- Root cause analysis
- Data explanation
- Metric deviation analysis
- Pattern recognition
- Alert investigation
"""

from typing import Any

from .base_specialist import BaseSpecialist


class AnomalyExplanationAgent(BaseSpecialist):
    """Anomaly explanation specialist focused on investigating and explaining metric anomalies."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize Anomaly Explanation agent."""
        super().__init__(
            role="anomaly-explanation",
            name="Anomaly Explanation",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get Anomaly Explanation domain expertise description."""
        return """Anomaly detection and investigation, root cause analysis for metric deviations,
data explanation and narrative, metric spike/drop analysis,
pattern recognition in data, alert investigation and triage,
correlation analysis, and anomaly impact assessment."""
