"""
Program Management Agent.

Expertise in:
- Program coordination
- Multi-project management
- Cross-functional programs
- Program tracking
- Stakeholder management
- Program governance
"""

from typing import Any

from .base_specialist import BaseSpecialist


class ProgramManagementAgent(BaseSpecialist):
    """Program management specialist focused on coordinating complex multi-project programs."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize Program Management agent."""
        super().__init__(
            role="program-management",
            name="Program Management",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get Program Management domain expertise description."""
        return """Program coordination and oversight, multi-project management,
cross-functional program execution, program milestone tracking,
stakeholder communication, program governance frameworks,
dependency management, resource coordination across projects,
and program risk identification."""
