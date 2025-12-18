"""
Business Operations Specialist Agent.

Expertise in:
- Process optimization
- Operations planning
- Vendor management
- Business analytics
- Project management
- Strategic initiatives
"""

from typing import Any

from .base_specialist import BaseSpecialist


class BusinessOperationsAgent(BaseSpecialist):
    """Business Operations specialist focused on operational efficiency and execution."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize business operations agent."""
        super().__init__(
            role="business-operations",
            name="Business Operations Specialist",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get business operations domain expertise description."""
        return """Process optimization and automation, operations planning and execution, vendor and partner management,
business analytics and reporting, project management and coordination, strategic initiatives and OKRs,
cross-functional collaboration, business intelligence, operational metrics and KPIs, resource allocation,
and operational excellence."""
