"""
Backend Developer Agent.

Expertise in:
- Services development
- API design
- Business logic
- Scalability
- Backend architecture
- Data processing
"""

from typing import Any

from .base_specialist import BaseSpecialist


class BackendDeveloperAgent(BaseSpecialist):
    """Backend Developer specialist focused on services, APIs, business logic, and scalability."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize backend developer agent."""
        super().__init__(
            role="backend-developer",
            name="Backend Developer Specialist",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get backend developer domain expertise description."""
        return """Services development, API design (REST, GraphQL, gRPC), business logic implementation,
scalability patterns, backend architecture, data processing, microservices,
authentication/authorization, caching strategies, message queues, background jobs,
database integration, API documentation, and backend performance optimization."""
