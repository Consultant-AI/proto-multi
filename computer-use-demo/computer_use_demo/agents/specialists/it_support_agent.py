"""
IT Support Agent.

Expertise in:
- Account management
- Device provisioning
- Access control
- Troubleshooting
- Help desk
- IT policies
"""

from typing import Any

from .base_specialist import BaseSpecialist


class ITSupportAgent(BaseSpecialist):
    """IT Support specialist focused on accounts, devices, access, and troubleshooting."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize IT support agent."""
        super().__init__(
            role="it-support",
            name="IT Support Specialist",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get IT support domain expertise description."""
        return """Account management, device provisioning, access control, troubleshooting,
help desk operations, IT policies, password resets, software installation,
network troubleshooting, VPN setup, email configuration, hardware support,
IT onboarding/offboarding, and remote support."""
