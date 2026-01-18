"""
Build & CI Agent.

Expertise in:
- CI/CD pipelines
- Build optimization
- Caching strategies
- Artifact management
- Build automation
- Pipeline design
"""

from typing import Any

from .base_specialist import BaseSpecialist


class BuildCIAgent(BaseSpecialist):
    """Build & CI specialist focused on pipelines, build speed, caching, and artifacts."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize build & CI agent."""
        super().__init__(
            role="build-ci",
            name="Build & CI Specialist",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get build & CI domain expertise description."""
        return """CI/CD pipelines (GitHub Actions, GitLab CI, Jenkins), build optimization,
caching strategies, artifact management, build automation, pipeline design,
parallel builds, dependency caching, build metrics, flaky test detection,
build notifications, environment management, and build security."""
