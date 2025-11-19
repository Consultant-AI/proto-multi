"""
Legal Compliance Specialist Agent.

Expertise in:
- Contract review and drafting
- Privacy compliance
- Terms of service
- Intellectual property
- Regulatory compliance
- Risk management
"""

from typing import Any

from .base_specialist import BaseSpecialist


class LegalComplianceAgent(BaseSpecialist):
    """Legal Compliance specialist focused on legal and regulatory matters."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None):
        """Initialize legal compliance agent."""
        super().__init__(
            role="legal-compliance",
            name="Legal Compliance Specialist",
            session_id=session_id,
            tools=tools,
        )

    def get_domain_expertise(self) -> str:
        """Get legal compliance domain expertise description."""
        return """Contract review and drafting, privacy compliance (GDPR, CCPA, privacy policies),
terms of service and user agreements, intellectual property (trademarks, copyrights, patents),
regulatory compliance, risk management and mitigation, data protection and security compliance,
vendor agreements, employment law, corporate governance, and legal documentation."""
