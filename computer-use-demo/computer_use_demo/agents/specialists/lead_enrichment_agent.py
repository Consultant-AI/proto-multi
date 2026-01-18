"""
Lead Enrichment Agent.

Expertise in:
- Firmographics research
- Intent data analysis
- Contact data collection
- Lead scoring
- Data enrichment
- Lead qualification data
"""

from typing import Any

from .base_specialist import BaseSpecialist


class LeadEnrichmentAgent(BaseSpecialist):
    """Lead Enrichment specialist focused on firmographics, intent, and contact data."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize lead enrichment agent."""
        super().__init__(
            role="lead-enrichment",
            name="Lead Enrichment Specialist",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get lead enrichment domain expertise description."""
        return """Firmographics research, intent data analysis, contact data collection,
lead scoring models, data enrichment tools (ZoomInfo, Clearbit, Apollo),
lead qualification data, company research, technographics, buying signals,
data accuracy verification, and enrichment automation."""
