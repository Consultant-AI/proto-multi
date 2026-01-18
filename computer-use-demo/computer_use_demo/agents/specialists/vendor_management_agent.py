"""
Vendor Management Agent.

Expertise in:
- Vendor selection
- Performance tracking
- Contract renewals
- Vendor relationships
- SLA monitoring
- Vendor risk assessment
"""

from typing import Any

from .base_specialist import BaseSpecialist


class VendorManagementAgent(BaseSpecialist):
    """Vendor Management specialist focused on selection, performance, and renewals."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize vendor management agent."""
        super().__init__(
            role="vendor-management",
            name="Vendor Management Specialist",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get vendor management domain expertise description."""
        return """Vendor selection, performance tracking, contract renewals, vendor relationships,
SLA monitoring, vendor risk assessment, vendor scorecards, supplier diversity,
vendor consolidation, relationship management, vendor communication,
escalation procedures, and vendor audits."""
