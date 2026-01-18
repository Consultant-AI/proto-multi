"""
SDR/Qualification Agent.

Expertise in:
- Discovery questions
- Fit scoring
- Lead qualification
- Meeting scheduling
- Opportunity creation
- BANT qualification
"""

from typing import Any

from .base_specialist import BaseSpecialist


class SDRQualificationAgent(BaseSpecialist):
    """SDR/Qualification specialist focused on discovery questions and fit scoring."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize SDR/qualification agent."""
        super().__init__(
            role="sdr-qualification",
            name="SDR / Qualification Specialist",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get SDR/qualification domain expertise description."""
        return """Discovery questions, fit scoring, lead qualification frameworks (BANT, MEDDIC, GPCT),
meeting scheduling, opportunity creation, qualification criteria, ICP matching,
objection handling, initial needs assessment, handoff to AE, and qualification reporting."""
