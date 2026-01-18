"""
Feature Flag Manager Agent.

Expertise in:
- Feature flags
- Toggle management
- Gradual rollouts
- Kill switches
- Flag lifecycle
- Targeting rules
"""

from typing import Any

from .base_specialist import BaseSpecialist


class FeatureFlagAgent(BaseSpecialist):
    """Feature flag manager specialist focused on feature flag management."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize Feature Flag agent."""
        super().__init__(
            role="feature-flag",
            name="Feature Flag Manager",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get Feature Flag Manager domain expertise description."""
        return """Feature flag management and lifecycle, toggle configuration,
gradual rollout strategies, kill switch implementation,
flag cleanup and hygiene, targeting rule design,
flag dependency management, and rollout coordination."""
