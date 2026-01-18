"""
Release Agent.

Expertise in:
- Versioning
- Rollout plans
- Canary deployments
- Rollback procedures
- Release coordination
- Changelog management
"""

from typing import Any

from .base_specialist import BaseSpecialist


class ReleaseAgent(BaseSpecialist):
    """Release specialist focused on versioning, rollout plans, canary deployments, and rollback."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize release agent."""
        super().__init__(
            role="release",
            name="Release Specialist",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get release domain expertise description."""
        return """Semantic versioning, rollout plans, canary deployments, rollback procedures,
release coordination, changelog management, release notes, feature flags for releases,
blue-green deployments, progressive rollouts, release automation, release validation,
hotfix procedures, and release communication."""
