"""
Message Bus abstraction.

Provides a unified interface for inter-computer communication.
Supports multiple backends (Redis, NATS, in-memory for testing).
"""

import asyncio
import threading
from abc import ABC, abstractmethod
from typing import Any, Callable, Coroutine

from .types import Message, MessageType


# Type alias for message handlers
MessageHandler = Callable[[Message], Coroutine[Any, Any, None]]


class MessageBusBackend(ABC):
    """Abstract base class for message bus backends."""

    @abstractmethod
    async def connect(self) -> None:
        """Connect to the message broker."""
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """Disconnect from the message broker."""
        pass

    @abstractmethod
    async def publish(self, channel: str, message: Message) -> None:
        """Publish a message to a channel."""
        pass

    @abstractmethod
    async def subscribe(self, channel: str, handler: MessageHandler) -> None:
        """Subscribe to a channel with a handler."""
        pass

    @abstractmethod
    async def unsubscribe(self, channel: str) -> None:
        """Unsubscribe from a channel."""
        pass

    @abstractmethod
    def is_connected(self) -> bool:
        """Check if connected to the broker."""
        pass


class InMemoryBackend(MessageBusBackend):
    """
    In-memory backend for testing and single-computer scenarios.

    Messages are delivered immediately within the same process.
    """

    def __init__(self):
        self._handlers: dict[str, list[MessageHandler]] = {}
        self._connected = False
        self._lock = threading.Lock()

    async def connect(self) -> None:
        self._connected = True

    async def disconnect(self) -> None:
        self._connected = False
        with self._lock:
            self._handlers.clear()

    async def publish(self, channel: str, message: Message) -> None:
        if not self._connected:
            raise RuntimeError("Not connected")

        with self._lock:
            handlers = self._handlers.get(channel, []).copy()

        # Deliver to all handlers
        for handler in handlers:
            try:
                await handler(message)
            except Exception as e:
                print(f"[MessageBus] Handler error: {e}")

    async def subscribe(self, channel: str, handler: MessageHandler) -> None:
        if not self._connected:
            raise RuntimeError("Not connected")

        with self._lock:
            if channel not in self._handlers:
                self._handlers[channel] = []
            self._handlers[channel].append(handler)

    async def unsubscribe(self, channel: str) -> None:
        with self._lock:
            self._handlers.pop(channel, None)

    def is_connected(self) -> bool:
        return self._connected


class MessageBus:
    """
    High-level message bus for inter-computer communication.

    Features:
    - Publish/subscribe messaging
    - Request/response patterns
    - Message routing by type
    - Automatic reconnection
    """

    def __init__(
        self,
        backend: MessageBusBackend | None = None,
        computer_id: str = "",
    ):
        self._backend = backend or InMemoryBackend()
        self._computer_id = computer_id
        self._type_handlers: dict[MessageType, list[MessageHandler]] = {}
        self._pending_responses: dict[str, asyncio.Future] = {}
        self._lock = threading.Lock()

    @property
    def computer_id(self) -> str:
        return self._computer_id

    @computer_id.setter
    def computer_id(self, value: str) -> None:
        self._computer_id = value

    async def connect(self) -> None:
        """Connect to the message broker."""
        await self._backend.connect()

        # Subscribe to computer-specific channel
        if self._computer_id:
            await self._backend.subscribe(
                f"computer:{self._computer_id}",
                self._handle_message,
            )

        # Subscribe to broadcast channel
        await self._backend.subscribe("broadcast", self._handle_message)

    async def disconnect(self) -> None:
        """Disconnect from the message broker."""
        await self._backend.disconnect()

        # Cancel pending responses
        with self._lock:
            for future in self._pending_responses.values():
                future.cancel()
            self._pending_responses.clear()

    def is_connected(self) -> bool:
        """Check if connected."""
        return self._backend.is_connected()

    async def publish(
        self,
        message: Message,
        channel: str | None = None,
    ) -> None:
        """
        Publish a message.

        Args:
            message: Message to publish
            channel: Optional channel (defaults to target computer or broadcast)
        """
        # Set source if not set
        if not message.source:
            message.source = self._computer_id

        # Determine channel
        if channel is None:
            if message.target:
                channel = f"computer:{message.target}"
            else:
                channel = "broadcast"

        await self._backend.publish(channel, message)

    async def request(
        self,
        message: Message,
        timeout: float = 30.0,
    ) -> Message | None:
        """
        Send a request and wait for response.

        Args:
            message: Request message
            timeout: Timeout in seconds

        Returns:
            Response message or None if timeout
        """
        # Generate correlation ID
        correlation_id = message.id
        message.correlation_id = correlation_id
        message.reply_to = f"computer:{self._computer_id}"

        # Create future for response
        future: asyncio.Future[Message] = asyncio.get_event_loop().create_future()
        with self._lock:
            self._pending_responses[correlation_id] = future

        try:
            # Send request
            await self.publish(message)

            # Wait for response
            return await asyncio.wait_for(future, timeout)

        except asyncio.TimeoutError:
            return None

        finally:
            with self._lock:
                self._pending_responses.pop(correlation_id, None)

    def on(self, message_type: MessageType, handler: MessageHandler) -> None:
        """
        Register a handler for a message type.

        Args:
            message_type: Type of message to handle
            handler: Async handler function
        """
        with self._lock:
            if message_type not in self._type_handlers:
                self._type_handlers[message_type] = []
            self._type_handlers[message_type].append(handler)

    def off(self, message_type: MessageType, handler: MessageHandler) -> None:
        """Remove a handler for a message type."""
        with self._lock:
            if message_type in self._type_handlers:
                try:
                    self._type_handlers[message_type].remove(handler)
                except ValueError:
                    pass

    async def _handle_message(self, message: Message) -> None:
        """Internal message handler."""
        # Check if this is a response to a pending request
        if message.correlation_id:
            with self._lock:
                future = self._pending_responses.get(message.correlation_id)
            if future and not future.done():
                future.set_result(message)
                return

        # Check if message is expired
        if message.is_expired():
            return

        # Route to type handlers
        with self._lock:
            handlers = self._type_handlers.get(message.type, []).copy()

        for handler in handlers:
            try:
                await handler(message)
            except Exception as e:
                print(f"[MessageBus] Handler error for {message.type}: {e}")


# Global message bus instance
_global_bus: MessageBus | None = None


def get_message_bus(
    backend: MessageBusBackend | None = None,
    computer_id: str = "",
) -> MessageBus:
    """Get or create the global message bus."""
    global _global_bus

    if _global_bus is None:
        _global_bus = MessageBus(backend, computer_id)

    return _global_bus


async def initialize_message_bus(
    backend: MessageBusBackend | None = None,
    computer_id: str = "",
) -> MessageBus:
    """Initialize and connect the global message bus."""
    bus = get_message_bus(backend, computer_id)
    await bus.connect()
    return bus


async def shutdown_message_bus() -> None:
    """Shutdown the global message bus."""
    global _global_bus

    if _global_bus:
        await _global_bus.disconnect()
        _global_bus = None
