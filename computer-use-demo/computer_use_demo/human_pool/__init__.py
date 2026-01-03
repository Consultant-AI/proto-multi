"""
Proto Human Pool Module - Delegate tasks to humans.

Manages a pool of humans for task delegation when:
- Tasks require physical action
- Legal/compliance review needed
- Emotional intelligence required
- Tasks exceed agent capabilities

Configuration stored in ~/.proto/company/humans/:
- pool.json: Registered humans
- requests/: Pending requests
- completed/: Completed requests (audit trail)

Usage:
    from computer_use_demo.human_pool import (
        get_human_pool_manager,
        Human,
        HumanRequest,
        RequestPriority,
    )

    # Get manager
    manager = get_human_pool_manager()

    # Register a human
    human = Human(
        id="alice",
        name="Alice Smith",
        email="alice@example.com",
        skills=["legal", "compliance"],
    )
    manager.register_human(human)

    # Create a request
    request = manager.create_request(
        title="Review contract",
        description="Need legal review of vendor contract",
        priority=RequestPriority.HIGH,
        required_skills=["legal"],
        sla_hours=24,
    )

    # Check for escalations
    escalated = manager.check_escalations()
"""

from .manager import (
    HumanPoolManager,
    get_human_pool_manager,
    get_humans_dir,
)

from .notification import (
    EmailNotificationSender,
    NotificationManager,
    NotificationSender,
    SlackNotificationSender,
    WebhookNotificationSender,
    get_notification_manager,
)

from .types import (
    EscalationRule,
    Human,
    HumanRequest,
    NotificationChannel,
    RequestPriority,
    RequestStatus,
)

__all__ = [
    # Types
    "EscalationRule",
    "Human",
    "HumanRequest",
    "NotificationChannel",
    "RequestPriority",
    "RequestStatus",
    # Manager
    "HumanPoolManager",
    "get_human_pool_manager",
    "get_humans_dir",
    # Notification
    "EmailNotificationSender",
    "NotificationManager",
    "NotificationSender",
    "SlackNotificationSender",
    "WebhookNotificationSender",
    "get_notification_manager",
]
