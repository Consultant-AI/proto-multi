"""
Proto Messaging Module.

Provides inter-computer communication through a message bus abstraction.

Supported Backends:
- InMemory (default, single-process)
- Redis Pub/Sub (distributed)

Usage:
    from computer_use_demo.messaging import (
        get_message_bus,
        Message,
        MessageType,
    )

    # Get the global message bus
    bus = get_message_bus()

    # Subscribe to messages
    async def handler(msg: Message):
        print(f"Received: {msg}")

    await bus.subscribe("tasks", handler)

    # Publish a message
    msg = Message(
        type=MessageType.TASK_ASSIGN,
        payload={"task": "do_something"},
        source="computer-1",
        target="computer-2",
    )
    await bus.publish("tasks", msg)
"""

from .bus import (
    InMemoryBackend,
    MessageBus,
    MessageBusBackend,
    MessageHandler,
    get_message_bus,
    shutdown_message_bus,
)

from .redis_backend import RedisBackend

from .types import (
    Message,
    MessageType,
    TaskAssignPayload,
    TaskCompletePayload,
    TaskFailPayload,
    HeartbeatPayload,
    KnowledgeUpdatePayload,
    QueryPayload,
    QueryResponsePayload,
    DelegationPayload,
    DelegationResultPayload,
)

__all__ = [
    # Types
    "Message",
    "MessageType",
    "TaskAssignPayload",
    "TaskCompletePayload",
    "TaskFailPayload",
    "HeartbeatPayload",
    "KnowledgeUpdatePayload",
    "QueryPayload",
    "QueryResponsePayload",
    "DelegationPayload",
    "DelegationResultPayload",
    # Bus
    "MessageBus",
    "MessageBusBackend",
    "MessageHandler",
    "InMemoryBackend",
    "RedisBackend",
    "get_message_bus",
    "shutdown_message_bus",
]
