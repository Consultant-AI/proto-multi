"""
Fraud Detection Agent.

Expertise in:
- Suspicious transactions
- Financial controls
- Anomaly detection
- Fraud prevention
- Risk indicators
- Investigation support
"""

from typing import Any

from .base_specialist import BaseSpecialist


class FraudDetectionAgent(BaseSpecialist):
    """Fraud Detection specialist focused on suspicious transactions and controls."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize fraud detection agent."""
        super().__init__(
            role="fraud-detection",
            name="Fraud Detection Specialist",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get fraud detection domain expertise description."""
        return """Suspicious transaction identification, financial controls, anomaly detection,
fraud prevention, risk indicators, investigation support, transaction monitoring,
pattern recognition, fraud alerts, control testing, segregation of duties,
and fraud risk assessment."""
