"""
Redis Pub/Sub backend for the message bus.

Uses Redis for distributed messaging across multiple computers.
"""

import asyncio
import threading
from typing import Any

from .bus import MessageBusBackend, MessageHandler
from .types import Message


class RedisBackend(MessageBusBackend):
    """
    Redis Pub/Sub backend for distributed messaging.

    Requires redis-py with async support:
        pip install redis[hiredis]

    Configuration:
        backend = RedisBackend(
            host="localhost",
            port=6379,
            password="secret",
            db=0,
        )
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        password: str | None = None,
        db: int = 0,
        ssl: bool = False,
        channel_prefix: str = "proto:",
        reconnect_delay: float = 5.0,
    ):
        self._host = host
        self._port = port
        self._password = password
        self._db = db
        self._ssl = ssl
        self._channel_prefix = channel_prefix
        self._reconnect_delay = reconnect_delay

        self._redis: Any = None
        self._pubsub: Any = None
        self._connected = False
        self._handlers: dict[str, MessageHandler] = {}
        self._listener_task: asyncio.Task | None = None
        self._lock = threading.Lock()
        self._should_reconnect = True

    async def connect(self) -> None:
        """Connect to Redis."""
        try:
            import redis.asyncio as redis
        except ImportError:
            raise ImportError("Redis backend requires: pip install redis[hiredis]")

        self._redis = redis.Redis(
            host=self._host,
            port=self._port,
            password=self._password,
            db=self._db,
            ssl=self._ssl,
            decode_responses=True,
        )

        # Test connection
        await self._redis.ping()

        self._pubsub = self._redis.pubsub()
        self._connected = True
        self._should_reconnect = True

        # Start listener task
        self._listener_task = asyncio.create_task(self._listen())

        print(f"[Redis] Connected to {self._host}:{self._port}")

    async def disconnect(self) -> None:
        """Disconnect from Redis."""
        self._should_reconnect = False
        self._connected = False

        if self._listener_task:
            self._listener_task.cancel()
            try:
                await self._listener_task
            except asyncio.CancelledError:
                pass
            self._listener_task = None

        if self._pubsub:
            await self._pubsub.close()
            self._pubsub = None

        if self._redis:
            await self._redis.close()
            self._redis = None

        with self._lock:
            self._handlers.clear()

        print("[Redis] Disconnected")

    async def publish(self, channel: str, message: Message) -> None:
        """Publish a message to a channel."""
        if not self._connected or not self._redis:
            raise RuntimeError("Not connected to Redis")

        full_channel = f"{self._channel_prefix}{channel}"
        await self._redis.publish(full_channel, message.to_json())

    async def subscribe(self, channel: str, handler: MessageHandler) -> None:
        """Subscribe to a channel with a handler."""
        if not self._connected or not self._pubsub:
            raise RuntimeError("Not connected to Redis")

        full_channel = f"{self._channel_prefix}{channel}"

        with self._lock:
            self._handlers[full_channel] = handler

        await self._pubsub.subscribe(full_channel)
        print(f"[Redis] Subscribed to {channel}")

    async def unsubscribe(self, channel: str) -> None:
        """Unsubscribe from a channel."""
        if not self._pubsub:
            return

        full_channel = f"{self._channel_prefix}{channel}"

        with self._lock:
            self._handlers.pop(full_channel, None)

        await self._pubsub.unsubscribe(full_channel)

    def is_connected(self) -> bool:
        """Check if connected to Redis."""
        return self._connected

    async def _listen(self) -> None:
        """Background task to listen for messages."""
        while self._should_reconnect:
            try:
                if not self._pubsub:
                    await asyncio.sleep(self._reconnect_delay)
                    continue

                async for message in self._pubsub.listen():
                    if message["type"] == "message":
                        channel = message["channel"]
                        data = message["data"]

                        with self._lock:
                            handler = self._handlers.get(channel)

                        if handler:
                            try:
                                msg = Message.from_json(data)
                                await handler(msg)
                            except Exception as e:
                                print(f"[Redis] Handler error: {e}")

            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"[Redis] Listener error: {e}")
                self._connected = False

                if self._should_reconnect:
                    print(f"[Redis] Reconnecting in {self._reconnect_delay}s...")
                    await asyncio.sleep(self._reconnect_delay)

                    try:
                        await self.connect()
                        # Re-subscribe to channels
                        with self._lock:
                            channels = list(self._handlers.keys())
                        for channel in channels:
                            await self._pubsub.subscribe(channel)
                    except Exception as re:
                        print(f"[Redis] Reconnection failed: {re}")

    async def get_stats(self) -> dict[str, Any]:
        """Get Redis connection stats."""
        if not self._redis:
            return {"connected": False}

        try:
            info = await self._redis.info()
            return {
                "connected": self._connected,
                "redis_version": info.get("redis_version"),
                "connected_clients": info.get("connected_clients"),
                "used_memory_human": info.get("used_memory_human"),
                "pubsub_channels": info.get("pubsub_channels"),
            }
        except Exception:
            return {"connected": False}
