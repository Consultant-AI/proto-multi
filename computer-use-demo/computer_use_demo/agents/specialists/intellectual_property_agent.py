"""
Intellectual Property Agent.

Expertise in:
- Trademarks
- Licenses
- Open-source compliance
- IP protection
- Patent review
- IP portfolio
"""

from typing import Any

from .base_specialist import BaseSpecialist


class IntellectualPropertyAgent(BaseSpecialist):
    """IP specialist focused on trademarks, licenses, and open-source compliance."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize intellectual property agent."""
        super().__init__(
            role="intellectual-property",
            name="Intellectual Property Specialist",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get intellectual property domain expertise description."""
        return """Trademarks, software licenses, open-source compliance, IP protection,
patent review support, IP portfolio management, license compatibility,
trademark monitoring, copyright protection, IP documentation, license auditing,
and open-source license obligations."""
