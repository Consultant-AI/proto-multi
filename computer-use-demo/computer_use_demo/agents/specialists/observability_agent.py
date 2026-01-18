"""
Observability Agent.

Expertise in:
- Dashboard creation
- Alert management
- Anomaly detection
- Incident routing
- Metrics visualization
- System monitoring
"""

from typing import Any

from .base_specialist import BaseSpecialist


class ObservabilityAgent(BaseSpecialist):
    """Observability specialist focused on dashboards, alerts, anomaly detection, and incident routing."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize observability agent."""
        super().__init__(
            role="observability",
            name="Observability Specialist",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get observability domain expertise description."""
        return """Dashboard creation, alert management, anomaly detection, incident routing,
metrics visualization, system monitoring, log aggregation, distributed tracing,
performance monitoring, health checks, alert threshold tuning, on-call routing,
incident classification, observability best practices, and monitoring strategy."""
