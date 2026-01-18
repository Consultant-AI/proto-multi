"""
Usability Testing Agent.

Expertise in:
- Test plan creation
- Prototype testing
- User testing sessions
- Findings analysis
- Recommendations
- Usability metrics
"""

from typing import Any

from .base_specialist import BaseSpecialist


class UsabilityTestingAgent(BaseSpecialist):
    """Usability Testing specialist focused on test plans, prototypes, findings, and recommendations."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize usability testing agent."""
        super().__init__(
            role="usability-testing",
            name="Usability Testing Specialist",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get usability testing domain expertise description."""
        return """Test plan creation, prototype testing, user testing sessions, findings analysis,
recommendations development, usability metrics, task completion rates, error rates,
think-aloud protocols, moderated testing, unmoderated testing, heuristic evaluation,
usability benchmarking, test script writing, and participant recruitment."""
