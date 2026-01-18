"""
Roadmap Priority Agent.

Expertise in:
- Feature prioritization
- Roadmap planning
- Priority frameworks
- Stakeholder alignment
- Trade-off analysis
- Backlog management
"""

from typing import Any

from .base_specialist import BaseSpecialist


class RoadmapPriorityAgent(BaseSpecialist):
    """Roadmap priority specialist focused on feature prioritization and roadmap planning."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize Roadmap Priority agent."""
        super().__init__(
            role="roadmap-priority",
            name="Roadmap Priority",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get Roadmap Priority domain expertise description."""
        return """Feature prioritization and scoring, roadmap planning and sequencing,
priority framework application (RICE, ICE, etc.), stakeholder alignment on priorities,
trade-off analysis between features, backlog management and grooming,
dependency mapping, and resource-constrained planning."""
