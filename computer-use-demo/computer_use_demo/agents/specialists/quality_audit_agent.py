"""
Quality & Audit Agent.

Expertise in:
- Output quality checking
- Review processes
- Audit logging
- Quality assurance
- Compliance auditing
- Process verification
"""

from typing import Any

from .base_specialist import BaseSpecialist


class QualityAuditAgent(BaseSpecialist):
    """Quality & Audit specialist focused on checking outputs, running reviews, and maintaining audit logs."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize quality audit agent."""
        super().__init__(
            role="quality-audit",
            name="Quality & Audit Specialist",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get quality & audit domain expertise description."""
        return """Output quality checking, review processes, audit logging, quality assurance,
compliance auditing, process verification, quality metrics, audit trail maintenance,
defect tracking, quality standards enforcement, review checklists, audit reporting,
continuous quality improvement, and quality gate management."""
