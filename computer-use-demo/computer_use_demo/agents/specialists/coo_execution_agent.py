"""
COO / Execution Agent.

Expertise in:
- Turning strategic goals into actionable plans
- Tracking delivery and execution
- Operational excellence
- Cross-functional coordination
- Process optimization
- Resource management
"""

from typing import Any

from .base_specialist import BaseSpecialist


class COOExecutionAgent(BaseSpecialist):
    """COO/Execution specialist focused on operational delivery and execution management."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize COO execution agent."""
        super().__init__(
            role="coo-execution",
            name="COO / Execution Specialist",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get COO/execution domain expertise description."""
        return """Operational execution, turning strategic goals into actionable plans, delivery tracking,
execution management, cross-functional coordination, process optimization, resource allocation,
operational excellence, performance monitoring, bottleneck identification, workflow management,
team coordination, milestone tracking, and operational risk mitigation."""
