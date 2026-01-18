"""
Access Control Agent.

Expertise in:
- Least privilege
- Periodic access reviews
- Permission management
- Role-based access
- Identity management
- Access policies
"""

from typing import Any

from .base_specialist import BaseSpecialist


class AccessControlAgent(BaseSpecialist):
    """Access Control specialist focused on least privilege and periodic reviews."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize access control agent."""
        super().__init__(
            role="access-control",
            name="Access Control Specialist",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get access control domain expertise description."""
        return """Least privilege implementation, periodic access reviews, permission management,
role-based access control (RBAC), identity management, access policies,
access provisioning, access deprovisioning, privileged access management,
access logging, segregation of duties, and access certification."""
