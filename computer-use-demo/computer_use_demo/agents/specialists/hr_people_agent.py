"""
HR People Specialist Agent.

Expertise in:
- Recruitment and hiring
- Onboarding and training
- Performance management
- Compensation and benefits
- Employee engagement
- HR operations
"""

from typing import Any

from .base_specialist import BaseSpecialist


class HRPeopleAgent(BaseSpecialist):
    """HR People specialist focused on human resources and people operations."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize HR people agent."""
        super().__init__(
            role="hr-people",
            name="HR People Specialist",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get HR people domain expertise description."""
        return """Recruitment and hiring processes, onboarding and training programs, performance management
and reviews, compensation and benefits planning, employee engagement and culture, HR operations and policies,
talent development and succession planning, workforce planning, employee relations, diversity and inclusion,
HR analytics, and HRIS systems."""
