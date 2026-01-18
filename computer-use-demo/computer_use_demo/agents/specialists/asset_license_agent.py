"""
Asset/License Agent.

Expertise in:
- SaaS license management
- Software renewals
- Asset inventory
- License compliance
- Vendor contracts
- Cost tracking
"""

from typing import Any

from .base_specialist import BaseSpecialist


class AssetLicenseAgent(BaseSpecialist):
    """Asset/License specialist focused on SaaS licenses, renewals, and inventory."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize asset/license agent."""
        super().__init__(
            role="asset-license",
            name="Asset / License Specialist",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get asset/license domain expertise description."""
        return """SaaS license management, software renewals, asset inventory, license compliance,
vendor contracts, cost tracking, license optimization, usage monitoring,
renewal reminders, license auditing, software asset management, subscription tracking,
license allocation, and vendor relationship management."""
