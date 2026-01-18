"""
User Research Agent.

Expertise in:
- User interviews
- Survey design
- Insight synthesis
- Persona development
- User behavior analysis
- Research methodology
"""

from typing import Any

from .base_specialist import BaseSpecialist


class UserResearchAgent(BaseSpecialist):
    """User Research specialist focused on interviews, surveys, insights synthesis, and personas."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize user research agent."""
        super().__init__(
            role="user-research",
            name="User Research Specialist",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get user research domain expertise description."""
        return """User interviews, survey design, insight synthesis, persona development,
user behavior analysis, research methodology, qualitative research, quantitative research,
user journey mapping, competitive user research, usability studies, research planning,
data collection, findings presentation, and actionable recommendations."""
