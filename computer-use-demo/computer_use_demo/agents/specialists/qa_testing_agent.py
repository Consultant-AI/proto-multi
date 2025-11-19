"""
QA Testing Specialist Agent.

Expertise in:
- Test planning and strategy
- Test case creation
- Automated testing
- Manual testing
- Bug tracking
- Quality assurance
"""

from typing import Any

from .base_specialist import BaseSpecialist


class QATestingAgent(BaseSpecialist):
    """QA Testing specialist focused on quality assurance and testing."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None):
        """Initialize QA testing agent."""
        super().__init__(
            role="qa-testing",
            name="QA Testing Specialist",
            session_id=session_id,
            tools=tools,
        )

    def get_domain_expertise(self) -> str:
        """Get QA testing domain expertise description."""
        return """Test planning and strategy, test case creation, automated testing (unit, integration, e2e),
manual testing, regression testing, performance testing, security testing, bug tracking and reporting,
test automation frameworks (Selenium, Cypress, Playwright), CI/CD testing, quality metrics,
test coverage analysis, and QA best practices."""
