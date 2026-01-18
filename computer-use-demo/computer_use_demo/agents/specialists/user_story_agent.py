"""
User Story Mapper Agent.

Expertise in:
- User story creation
- Story mapping
- Journey mapping
- Epic breakdown
- Story estimation
- Acceptance criteria
"""

from typing import Any

from .base_specialist import BaseSpecialist


class UserStoryAgent(BaseSpecialist):
    """User story mapper specialist focused on creating and organizing user stories."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize User Story agent."""
        super().__init__(
            role="user-story",
            name="User Story Mapper",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get User Story Mapper domain expertise description."""
        return """User story creation and refinement, story mapping techniques,
user journey mapping, epic breakdown into stories,
story point estimation, acceptance criteria writing,
persona-based story development, and backlog organization."""
