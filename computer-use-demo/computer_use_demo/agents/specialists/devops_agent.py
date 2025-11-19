"""
DevOps Specialist Agent.

Expertise in:
- Infrastructure as code
- CI/CD pipelines
- Container orchestration
- Cloud platforms
- Monitoring and logging
- System reliability
"""

from typing import Any

from .base_specialist import BaseSpecialist


class DevOpsAgent(BaseSpecialist):
    """DevOps specialist focused on infrastructure and deployment automation."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None):
        """Initialize DevOps agent."""
        super().__init__(
            role="devops",
            name="DevOps Specialist",
            session_id=session_id,
            tools=tools,
        )

    def get_domain_expertise(self) -> str:
        """Get DevOps domain expertise description."""
        return """Infrastructure as code (Terraform, CloudFormation), CI/CD pipelines (GitHub Actions, Jenkins),
container orchestration (Docker, Kubernetes), cloud platforms (AWS, GCP, Azure), monitoring and logging
(Prometheus, Grafana, ELK), system reliability (SRE practices), deployment strategies, configuration management,
security and compliance, incident response, and performance optimization."""
