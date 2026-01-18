"""
Quality Governance Agent.

Expertise in:
- Quality standards
- Governance frameworks
- Quality assurance
- Compliance monitoring
- Process quality
- Quality metrics
"""

from typing import Any

from .base_specialist import BaseSpecialist


class QualityGovernanceAgent(BaseSpecialist):
    """Quality governance specialist focused on maintaining quality standards and governance."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize Quality Governance agent."""
        super().__init__(
            role="quality-governance",
            name="Quality Governance",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get Quality Governance domain expertise description."""
        return """Quality standards definition and enforcement, governance framework design,
quality assurance processes, compliance monitoring,
process quality assessment, quality metrics tracking,
continuous improvement initiatives, and quality gate management."""
