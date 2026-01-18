"""
Glossary/Taxonomy Agent.

Expertise in:
- Terminology management
- Taxonomy design
- Glossary maintenance
- Term standardization
- Classification systems
- Vocabulary control
"""

from typing import Any

from .base_specialist import BaseSpecialist


class GlossaryTaxonomyAgent(BaseSpecialist):
    """Glossary/taxonomy specialist focused on terminology and classification management."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize Glossary/Taxonomy agent."""
        super().__init__(
            role="glossary-taxonomy",
            name="Glossary & Taxonomy",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get Glossary/Taxonomy domain expertise description."""
        return """Terminology management and standardization, taxonomy design and maintenance,
glossary curation, term definition and disambiguation,
classification system design, vocabulary control,
ontology development, and cross-team terminology alignment."""
