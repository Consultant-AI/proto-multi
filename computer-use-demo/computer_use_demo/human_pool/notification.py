"""
Notification system for human requests.

Supports multiple channels: email, Slack, SMS, webhooks.
"""

import json
from abc import ABC, abstractmethod
from typing import Any

from .types import Human, HumanRequest, NotificationChannel


class NotificationSender(ABC):
    """Base class for notification senders."""

    @abstractmethod
    async def send(
        self,
        human: Human,
        request: HumanRequest,
        message: str,
    ) -> bool:
        """
        Send a notification.

        Args:
            human: Target human
            request: Related request
            message: Notification message

        Returns:
            True if sent successfully
        """
        pass


class EmailNotificationSender(NotificationSender):
    """Send notifications via email."""

    def __init__(self, smtp_config: dict[str, Any] | None = None):
        self._smtp_config = smtp_config or {}

    async def send(
        self,
        human: Human,
        request: HumanRequest,
        message: str,
    ) -> bool:
        if not human.email:
            return False

        # TODO: Implement actual email sending
        # For now, just log
        print(f"[Email] Would send to {human.email}:")
        print(f"  Subject: {request.title}")
        print(f"  Body: {message}")
        return True


class SlackNotificationSender(NotificationSender):
    """Send notifications via Slack."""

    def __init__(self, webhook_url: str | None = None):
        self._webhook_url = webhook_url

    async def send(
        self,
        human: Human,
        request: HumanRequest,
        message: str,
    ) -> bool:
        if not human.slack_id:
            return False

        # TODO: Implement actual Slack sending
        # For now, just log
        print(f"[Slack] Would send to {human.slack_id}:")
        print(f"  Message: {message}")
        return True


class WebhookNotificationSender(NotificationSender):
    """Send notifications via webhook."""

    def __init__(self, url: str):
        self._url = url

    async def send(
        self,
        human: Human,
        request: HumanRequest,
        message: str,
    ) -> bool:
        # TODO: Implement actual webhook call
        # For now, just log
        print(f"[Webhook] Would POST to {self._url}:")
        print(f"  Request ID: {request.id}")
        print(f"  Message: {message}")
        return True


class NotificationManager:
    """
    Manages notification sending across channels.
    """

    def __init__(self):
        self._senders: dict[NotificationChannel, NotificationSender] = {
            NotificationChannel.EMAIL: EmailNotificationSender(),
            NotificationChannel.SLACK: SlackNotificationSender(),
        }

    def register_sender(
        self,
        channel: NotificationChannel,
        sender: NotificationSender,
    ) -> None:
        """Register a notification sender for a channel."""
        self._senders[channel] = sender

    async def notify(
        self,
        human: Human,
        request: HumanRequest,
        message: str | None = None,
        channel: NotificationChannel | None = None,
    ) -> bool:
        """
        Send a notification to a human.

        Args:
            human: Target human
            request: Related request
            message: Custom message (or auto-generated)
            channel: Specific channel (or use human's preferred)

        Returns:
            True if sent successfully
        """
        # Use preferred channel if not specified
        channel = channel or human.preferred_channel

        # Generate message if not provided
        if message is None:
            message = self._generate_message(request)

        # Get sender
        sender = self._senders.get(channel)
        if not sender:
            return False

        try:
            return await sender.send(human, request, message)
        except Exception as e:
            print(f"[Notification] Failed to send via {channel}: {e}")
            return False

    async def notify_assignment(
        self,
        human: Human,
        request: HumanRequest,
    ) -> bool:
        """Notify human of new assignment."""
        message = f"""
You have been assigned a new task:

Title: {request.title}
Priority: {request.priority.value.upper()}
{f"Deadline: {request.deadline}" if request.deadline else ""}

Description:
{request.description}

Please respond as soon as possible.
"""
        return await self.notify(human, request, message.strip())

    async def notify_escalation(
        self,
        human: Human,
        request: HumanRequest,
    ) -> bool:
        """Notify about an escalated request."""
        message = f"""
⚠️ ESCALATION: Task overdue

Title: {request.title}
Priority: {request.priority.value.upper()}
Created: {request.created_at}

This request has exceeded its SLA and requires immediate attention.

Description:
{request.description}
"""
        return await self.notify(human, request, message.strip())

    def _generate_message(self, request: HumanRequest) -> str:
        """Generate a default notification message."""
        return f"""
Task Request: {request.title}
Priority: {request.priority.value.upper()}
Status: {request.status.value}

{request.description}
"""


# Global notification manager
_notification_manager: NotificationManager | None = None


def get_notification_manager() -> NotificationManager:
    """Get the global notification manager."""
    global _notification_manager

    if _notification_manager is None:
        _notification_manager = NotificationManager()

    return _notification_manager
