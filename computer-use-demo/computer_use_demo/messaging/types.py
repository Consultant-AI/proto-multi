"""
Message types for inter-computer communication.
"""

import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class MessageType(str, Enum):
    """Types of messages in the system."""

    # Task management
    TASK_ASSIGN = "task_assign"
    TASK_COMPLETE = "task_complete"
    TASK_FAILED = "task_failed"
    TASK_PROGRESS = "task_progress"

    # Computer management
    HEARTBEAT = "heartbeat"
    COMPUTER_ONLINE = "computer_online"
    COMPUTER_OFFLINE = "computer_offline"
    COMPUTER_STATUS = "computer_status"

    # Knowledge sync
    KNOWLEDGE_UPDATE = "knowledge_update"
    KNOWLEDGE_SYNC_REQUEST = "knowledge_sync_request"
    KNOWLEDGE_SYNC_RESPONSE = "knowledge_sync_response"

    # Agent communication
    AGENT_MESSAGE = "agent_message"
    DELEGATION_REQUEST = "delegation_request"
    DELEGATION_RESPONSE = "delegation_response"

    # Query/Response
    QUERY = "query"
    QUERY_RESPONSE = "query_response"

    # System
    BROADCAST = "broadcast"
    PING = "ping"
    PONG = "pong"


class MessagePriority(int, Enum):
    """Message priority levels."""

    LOW = 1
    NORMAL = 5
    HIGH = 8
    URGENT = 10


@dataclass
class Message:
    """A message for inter-computer communication."""

    # Message type
    type: MessageType

    # Message payload
    payload: dict[str, Any]

    # Unique message ID
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    # Source computer ID
    source: str = ""

    # Target computer ID (empty for broadcast)
    target: str = ""

    # Priority
    priority: MessagePriority = MessagePriority.NORMAL

    # Timestamp
    timestamp: datetime = field(default_factory=datetime.utcnow)

    # Correlation ID (for request-response patterns)
    correlation_id: str | None = None

    # Reply-to channel (for responses)
    reply_to: str | None = None

    # TTL in seconds (0 = no expiry)
    ttl: int = 0

    def to_json(self) -> str:
        """Serialize to JSON."""
        return json.dumps({
            "id": self.id,
            "type": self.type.value,
            "payload": self.payload,
            "source": self.source,
            "target": self.target,
            "priority": self.priority.value,
            "timestamp": self.timestamp.isoformat(),
            "correlation_id": self.correlation_id,
            "reply_to": self.reply_to,
            "ttl": self.ttl,
        })

    @classmethod
    def from_json(cls, data: str) -> "Message":
        """Deserialize from JSON."""
        obj = json.loads(data)
        return cls(
            id=obj["id"],
            type=MessageType(obj["type"]),
            payload=obj["payload"],
            source=obj.get("source", ""),
            target=obj.get("target", ""),
            priority=MessagePriority(obj.get("priority", 5)),
            timestamp=datetime.fromisoformat(obj["timestamp"]),
            correlation_id=obj.get("correlation_id"),
            reply_to=obj.get("reply_to"),
            ttl=obj.get("ttl", 0),
        )

    def is_expired(self) -> bool:
        """Check if message has expired."""
        if self.ttl == 0:
            return False
        elapsed = (datetime.utcnow() - self.timestamp).total_seconds()
        return elapsed > self.ttl


@dataclass
class TaskAssignPayload:
    """Payload for TASK_ASSIGN messages."""

    task_id: str
    description: str
    assigned_agent: str
    project_name: str | None = None
    priority: str = "medium"
    context: dict[str, Any] = field(default_factory=dict)
    deadline: datetime | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "description": self.description,
            "assigned_agent": self.assigned_agent,
            "project_name": self.project_name,
            "priority": self.priority,
            "context": self.context,
            "deadline": self.deadline.isoformat() if self.deadline else None,
        }


@dataclass
class TaskCompletePayload:
    """Payload for TASK_COMPLETE messages."""

    task_id: str
    result: str
    success: bool = True
    iterations: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "result": self.result,
            "success": self.success,
            "iterations": self.iterations,
            "metadata": self.metadata,
        }


@dataclass
class HeartbeatPayload:
    """Payload for HEARTBEAT messages."""

    computer_id: str
    status: str = "healthy"
    cpu_percent: float = 0.0
    memory_percent: float = 0.0
    active_tasks: int = 0
    capabilities: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "computer_id": self.computer_id,
            "status": self.status,
            "cpu_percent": self.cpu_percent,
            "memory_percent": self.memory_percent,
            "active_tasks": self.active_tasks,
            "capabilities": self.capabilities,
        }


@dataclass
class KnowledgeUpdatePayload:
    """Payload for KNOWLEDGE_UPDATE messages."""

    entry_id: str
    title: str
    content: str
    knowledge_type: str
    project_name: str | None = None
    tags: list[str] = field(default_factory=list)
    source_computer: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "entry_id": self.entry_id,
            "title": self.title,
            "content": self.content,
            "knowledge_type": self.knowledge_type,
            "project_name": self.project_name,
            "tags": self.tags,
            "source_computer": self.source_computer,
        }


@dataclass
class TaskFailPayload:
    """Payload for TASK_FAILED messages."""

    task_id: str
    error: str
    error_type: str = "unknown"
    retry_count: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "error": self.error,
            "error_type": self.error_type,
            "retry_count": self.retry_count,
            "metadata": self.metadata,
        }


@dataclass
class QueryPayload:
    """Payload for query messages."""

    query_type: str
    query: str
    parameters: dict[str, Any] = field(default_factory=dict)
    timeout: float = 30.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "query_type": self.query_type,
            "query": self.query,
            "parameters": self.parameters,
            "timeout": self.timeout,
        }


@dataclass
class QueryResponsePayload:
    """Payload for query response messages."""

    query_id: str
    success: bool
    result: Any = None
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "query_id": self.query_id,
            "success": self.success,
            "result": self.result,
            "error": self.error,
        }


@dataclass
class DelegationPayload:
    """Payload for DELEGATION_REQUEST messages."""

    delegation_id: str
    task_description: str
    required_capabilities: list[str] = field(default_factory=list)
    priority: str = "medium"
    timeout: float = 3600.0
    context: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "delegation_id": self.delegation_id,
            "task_description": self.task_description,
            "required_capabilities": self.required_capabilities,
            "priority": self.priority,
            "timeout": self.timeout,
            "context": self.context,
        }


@dataclass
class DelegationResultPayload:
    """Payload for DELEGATION_RESPONSE messages."""

    delegation_id: str
    accepted: bool
    result: Any = None
    error: str | None = None
    computer_id: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "delegation_id": self.delegation_id,
            "accepted": self.accepted,
            "result": self.result,
            "error": self.error,
            "computer_id": self.computer_id,
        }
