"""
Security Specialist Agent.

Expertise in:
- Application security
- Infrastructure security
- Security compliance
- Threat modeling
- Vulnerability assessment
- Incident response
"""

from typing import Any

from .base_specialist import BaseSpecialist


class SecurityAgent(BaseSpecialist):
    """Security specialist focused on application and infrastructure security."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None):
        """Initialize security agent."""
        super().__init__(
            role="security",
            name="Security Specialist",
            session_id=session_id,
            tools=tools,
        )

    def get_domain_expertise(self) -> str:
        """Get security domain expertise description."""
        return """Application security (OWASP, secure coding), infrastructure security, security compliance
(SOC 2, ISO 27001, GDPR), threat modeling and risk assessment, vulnerability assessment and penetration testing,
incident response and forensics, security monitoring and SIEM, access control and identity management,
encryption and data protection, security audits, and DevSecOps practices."""
