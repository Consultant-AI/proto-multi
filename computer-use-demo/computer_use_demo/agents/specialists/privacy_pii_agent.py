"""
Privacy/PII Agent.

Expertise in:
- Data minimization
- Retention policies
- PII redaction
- Privacy compliance
- Data anonymization
- Consent management
"""

from typing import Any

from .base_specialist import BaseSpecialist


class PrivacyPIIAgent(BaseSpecialist):
    """Privacy/PII specialist focused on data minimization, retention policies, and redaction."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize privacy/PII agent."""
        super().__init__(
            role="privacy-pii",
            name="Privacy / PII Specialist",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get privacy/PII domain expertise description."""
        return """Data minimization, retention policies, PII redaction, privacy compliance (GDPR, CCPA),
data anonymization, consent management, data subject requests, privacy impact assessments,
data classification, encryption requirements, data masking, pseudonymization,
privacy by design, and data deletion workflows."""
