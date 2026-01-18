"""
Weekly Brief ("What Changed This Week?") Agent.

Expertise in:
- Weekly summaries
- Change tracking
- Progress reporting
- Highlight identification
- Executive updates
- Trend spotting
"""

from typing import Any

from .base_specialist import BaseSpecialist


class WeeklyBriefAgent(BaseSpecialist):
    """Weekly brief specialist focused on summarizing key changes and updates."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize Weekly Brief agent."""
        super().__init__(
            role="weekly-brief",
            name="Weekly Brief",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get Weekly Brief domain expertise description."""
        return """Weekly summary creation and "what changed this week" briefings,
change tracking across departments, progress reporting and highlights,
key metric movement identification, executive update compilation,
trend spotting and pattern recognition, risk and opportunity flagging,
cross-functional update aggregation, and concise executive communication."""
