"""
Type definitions for the Human Pool system.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class RequestPriority(str, Enum):
    """Priority levels for human requests."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class RequestStatus(str, Enum):
    """Status of a human request."""

    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ESCALATED = "escalated"


class NotificationChannel(str, Enum):
    """Channels for notifying humans."""

    EMAIL = "email"
    SLACK = "slack"
    SMS = "sms"
    WEBHOOK = "webhook"


@dataclass
class Human:
    """A human in the pool."""

    # Unique identifier
    id: str

    # Display name
    name: str

    # Email address
    email: str | None = None

    # Phone number (for SMS)
    phone: str | None = None

    # Slack user ID
    slack_id: str | None = None

    # Skills/roles this human has
    skills: list[str] = field(default_factory=list)

    # Preferred notification channel
    preferred_channel: NotificationChannel = NotificationChannel.EMAIL

    # Whether human is available
    available: bool = True

    # Current workload (number of active requests)
    workload: int = 0

    # Maximum concurrent requests
    max_workload: int = 5


@dataclass
class HumanRequest:
    """A request for human assistance."""

    # Unique request ID
    id: str

    # Request title/summary
    title: str

    # Detailed description
    description: str

    # Priority level
    priority: RequestPriority = RequestPriority.MEDIUM

    # Current status
    status: RequestStatus = RequestStatus.PENDING

    # Required skills
    required_skills: list[str] = field(default_factory=list)

    # Assigned human ID (if assigned)
    assigned_to: str | None = None

    # Agent that created this request
    created_by: str | None = None

    # Project context
    project_name: str | None = None

    # Additional context
    context: dict[str, Any] = field(default_factory=dict)

    # Deadline (if any)
    deadline: datetime | None = None

    # SLA in hours (for auto-escalation)
    sla_hours: float | None = None

    # When request was created
    created_at: datetime = field(default_factory=datetime.utcnow)

    # When request was last updated
    updated_at: datetime = field(default_factory=datetime.utcnow)

    # When request was assigned
    assigned_at: datetime | None = None

    # When request was completed
    completed_at: datetime | None = None

    # Result/response from human
    result: str | None = None

    # Attachments (file paths)
    attachments: list[str] = field(default_factory=list)

    def is_overdue(self) -> bool:
        """Check if request has exceeded SLA."""
        if self.sla_hours is None:
            return False

        if self.status in [RequestStatus.COMPLETED, RequestStatus.CANCELLED]:
            return False

        elapsed = (datetime.utcnow() - self.created_at).total_seconds() / 3600
        return elapsed > self.sla_hours


@dataclass
class EscalationRule:
    """Rule for auto-escalating requests."""

    # Hours after which to escalate
    after_hours: float

    # New priority after escalation
    new_priority: RequestPriority

    # Additional notification recipients
    notify_additional: list[str] = field(default_factory=list)

    # Custom message
    message: str = ""
