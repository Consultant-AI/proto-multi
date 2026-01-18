"""
Monitoring Agent.

Expertise in:
- Log management
- Metrics collection
- Trace analysis
- Alert tuning
- Dashboard design
- APM integration
"""

from typing import Any

from .base_specialist import BaseSpecialist


class MonitoringAgent(BaseSpecialist):
    """Monitoring specialist focused on logs, metrics, traces, alert tuning, and dashboards."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize monitoring agent."""
        super().__init__(
            role="monitoring",
            name="Monitoring Specialist",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get monitoring domain expertise description."""
        return """Log management (ELK, Splunk), metrics collection (Prometheus, Datadog),
trace analysis (Jaeger, Zipkin), alert tuning, dashboard design (Grafana),
APM integration, log aggregation, metric visualization, anomaly detection setup,
alert fatigue reduction, monitoring strategy, and observability pipelines."""
