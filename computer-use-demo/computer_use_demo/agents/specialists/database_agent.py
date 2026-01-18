"""
Database Agent.

Expertise in:
- Schema design
- Migrations
- Indexing
- Query tuning
- Database optimization
- Data modeling
"""

from typing import Any

from .base_specialist import BaseSpecialist


class DatabaseAgent(BaseSpecialist):
    """Database specialist focused on schema design, migrations, indexing, and query tuning."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize database agent."""
        super().__init__(
            role="database",
            name="Database Specialist",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get database domain expertise description."""
        return """Schema design, database migrations, indexing strategies, query tuning,
database optimization, data modeling, normalization/denormalization, SQL and NoSQL databases,
PostgreSQL, MySQL, MongoDB, Redis, database replication, sharding, backup strategies,
query analysis, database security, and ORM optimization."""
