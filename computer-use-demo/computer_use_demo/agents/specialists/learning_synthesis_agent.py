"""
Learning Synthesis Agent.

Expertise in:
- Knowledge synthesis
- Cross-experiment learning
- Pattern identification
- Best practice extraction
- Learning documentation
- Institutional memory
"""

from typing import Any

from .base_specialist import BaseSpecialist


class LearningSynthesisAgent(BaseSpecialist):
    """Learning synthesis specialist focused on extracting learnings across experiments."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize Learning Synthesis agent."""
        super().__init__(
            role="learning-synthesis",
            name="Learning Synthesis",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get Learning Synthesis domain expertise description."""
        return """Knowledge synthesis across experiments, cross-experiment pattern identification,
best practice extraction, learning documentation and sharing,
institutional memory building, meta-analysis of experiments,
failure pattern recognition, and organizational learning facilitation."""
