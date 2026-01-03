"""
Knowledge Synchronization Engine.

Handles syncing knowledge across multiple computers.
"""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable

from .types import (
    ConflictResolution,
    KnowledgeItem,
    KnowledgeScope,
    SyncStatus,
)
from .store import KnowledgeStore


class SyncDirection(str, Enum):
    """Direction of synchronization."""

    PUSH = "push"  # Send to others
    PULL = "pull"  # Receive from others
    BIDIRECTIONAL = "bidirectional"


@dataclass
class SyncEvent:
    """Event during synchronization."""

    # Type of event
    event_type: str  # "push", "pull", "conflict", "error"

    # Affected key
    key: str

    # Source computer
    source: str | None = None

    # Target computer
    target: str | None = None

    # Event details
    details: dict[str, Any] = field(default_factory=dict)

    # Timestamp
    timestamp: datetime = field(default_factory=datetime.utcnow)


# Type for sync event callbacks
SyncEventCallback = Callable[[SyncEvent], None]


class KnowledgeSyncEngine:
    """
    Synchronizes knowledge across multiple computers.

    Features:
    - Push/pull synchronization
    - Conflict detection and resolution
    - Delta sync (only changed items)
    - Event notifications
    """

    def __init__(
        self,
        store: KnowledgeStore,
        computer_id: str,
        sync_interval: float = 30.0,
    ):
        self._store = store
        self._computer_id = computer_id
        self._sync_interval = sync_interval

        # State tracking
        self._last_sync: dict[str, datetime] = {}  # computer_id -> last sync time
        self._pending_pushes: list[str] = []  # Keys to push

        # Message bus (will be injected)
        self._message_bus = None

        # Callbacks
        self._event_callbacks: list[SyncEventCallback] = []

        # Background tasks
        self._running = False
        self._sync_task: asyncio.Task | None = None

        # Register store callback
        self._store.on_change(self._on_local_change)

    def set_message_bus(self, bus: Any) -> None:
        """Set the message bus for communication."""
        self._message_bus = bus

    async def start(self) -> None:
        """Start the sync engine."""
        self._running = True
        self._sync_task = asyncio.create_task(self._sync_loop())

        # Subscribe to sync messages
        if self._message_bus:
            await self._message_bus.subscribe(
                f"knowledge.sync.{self._computer_id}",
                self._handle_sync_message,
            )
            await self._message_bus.subscribe(
                "knowledge.sync.broadcast",
                self._handle_sync_message,
            )

        print("[Sync] Engine started")

    async def stop(self) -> None:
        """Stop the sync engine."""
        self._running = False

        if self._sync_task:
            self._sync_task.cancel()
            try:
                await self._sync_task
            except asyncio.CancelledError:
                pass

        print("[Sync] Engine stopped")

    async def sync(
        self,
        direction: SyncDirection = SyncDirection.BIDIRECTIONAL,
        target: str | None = None,
    ) -> dict[str, Any]:
        """
        Perform synchronization.

        Args:
            direction: Sync direction
            target: Specific computer to sync with (or all)

        Returns:
            Sync statistics
        """
        stats = {
            "pushed": 0,
            "pulled": 0,
            "conflicts": 0,
            "errors": 0,
        }

        if direction in [SyncDirection.PUSH, SyncDirection.BIDIRECTIONAL]:
            push_stats = await self._push_changes(target)
            stats["pushed"] = push_stats["count"]
            stats["errors"] += push_stats["errors"]

        if direction in [SyncDirection.PULL, SyncDirection.BIDIRECTIONAL]:
            pull_stats = await self._pull_changes(target)
            stats["pulled"] = pull_stats["count"]
            stats["conflicts"] = pull_stats["conflicts"]
            stats["errors"] += pull_stats["errors"]

        return stats

    async def _push_changes(self, target: str | None = None) -> dict[str, int]:
        """Push local changes to other computers."""
        stats = {"count": 0, "errors": 0}

        if not self._message_bus:
            return stats

        # Get pending items
        pending = await self._store.get_pending_sync()

        for item in pending:
            try:
                # Skip local-only items
                if item.scope == KnowledgeScope.LOCAL:
                    continue

                # Check selective scope
                if item.scope == KnowledgeScope.SELECTIVE:
                    if target and target not in item.allowed_computers:
                        continue

                # Send sync message
                from ..messaging import Message, MessageType

                channel = (
                    f"knowledge.sync.{target}"
                    if target
                    else "knowledge.sync.broadcast"
                )

                msg = Message(
                    type=MessageType.KNOWLEDGE_UPDATE,
                    payload={
                        "operation": "update",
                        "item": item.to_dict(),
                    },
                    source=self._computer_id,
                    target=target or "broadcast",
                )

                await self._message_bus.publish(channel, msg)
                stats["count"] += 1

                # Emit event
                self._emit_event(SyncEvent(
                    event_type="push",
                    key=item.key,
                    source=self._computer_id,
                    target=target,
                ))

            except Exception as e:
                stats["errors"] += 1
                self._emit_event(SyncEvent(
                    event_type="error",
                    key=item.key,
                    details={"error": str(e)},
                ))

        # Mark as synced
        if stats["count"] > 0:
            await self._store.mark_synced([item.key for item in pending])

        return stats

    async def _pull_changes(self, source: str | None = None) -> dict[str, int]:
        """Request changes from other computers."""
        stats = {"count": 0, "conflicts": 0, "errors": 0}

        if not self._message_bus:
            return stats

        # Request sync from source
        from ..messaging import Message, MessageType

        channel = (
            f"knowledge.sync.{source}"
            if source
            else "knowledge.sync.broadcast"
        )

        # Get last sync time
        last_sync = self._last_sync.get(source or "broadcast", datetime.min)

        msg = Message(
            type=MessageType.QUERY,
            payload={
                "query_type": "knowledge_sync",
                "since": last_sync.isoformat(),
            },
            source=self._computer_id,
            target=source or "broadcast",
        )

        await self._message_bus.publish(channel, msg)

        # Note: Actual items will come via _handle_sync_message
        # Update last sync time
        self._last_sync[source or "broadcast"] = datetime.utcnow()

        return stats

    async def _handle_sync_message(self, msg: Any) -> None:
        """Handle incoming sync message."""
        try:
            # Skip our own messages
            if msg.source == self._computer_id:
                return

            payload = msg.payload

            if msg.type.value == "knowledge_update":
                await self._handle_knowledge_update(payload, msg.source)

            elif msg.type.value == "query":
                if payload.get("query_type") == "knowledge_sync":
                    await self._handle_sync_request(payload, msg.source)

            elif msg.type.value == "query_response":
                await self._handle_sync_response(payload, msg.source)

        except Exception as e:
            print(f"[Sync] Error handling message: {e}")

    async def _handle_knowledge_update(
        self,
        payload: dict[str, Any],
        source: str,
    ) -> None:
        """Handle a knowledge update from another computer."""
        item_data = payload.get("item")
        if not item_data:
            return

        remote_item = KnowledgeItem.from_dict(item_data)

        # Check visibility
        if not remote_item.is_visible_to(self._computer_id):
            return

        # Check for conflict
        local_item = await self._store.get(remote_item.key)

        if local_item:
            if local_item.hash != remote_item.hash:
                # Conflict detected
                resolved = await self._resolve_conflict(local_item, remote_item)

                if resolved:
                    await self._store.put(resolved, notify=False)
                    self._emit_event(SyncEvent(
                        event_type="conflict",
                        key=remote_item.key,
                        source=source,
                        details={
                            "resolution": resolved.conflict_resolution.value,
                            "winner": "remote" if resolved.hash == remote_item.hash else "local",
                        },
                    ))
            # Same hash - no action needed

        else:
            # New item
            remote_item.sync_status = SyncStatus.SYNCED
            await self._store.put(remote_item, notify=False)
            self._emit_event(SyncEvent(
                event_type="pull",
                key=remote_item.key,
                source=source,
            ))

    async def _handle_sync_request(
        self,
        payload: dict[str, Any],
        requester: str,
    ) -> None:
        """Handle a sync request from another computer."""
        since_str = payload.get("since")
        since = datetime.fromisoformat(since_str) if since_str else datetime.min

        # Get changes since timestamp
        items = await self._store.get_changes_since(since)

        # Filter for visibility
        visible_items = [
            item for item in items
            if item.is_visible_to(requester)
        ]

        # Send response
        if self._message_bus and visible_items:
            from ..messaging import Message, MessageType

            msg = Message(
                type=MessageType.QUERY_RESPONSE,
                payload={
                    "items": [item.to_dict() for item in visible_items],
                },
                source=self._computer_id,
                target=requester,
            )

            await self._message_bus.publish(
                f"knowledge.sync.{requester}",
                msg,
            )

    async def _handle_sync_response(
        self,
        payload: dict[str, Any],
        source: str,
    ) -> None:
        """Handle a sync response from another computer."""
        items_data = payload.get("items", [])

        for item_data in items_data:
            remote_item = KnowledgeItem.from_dict(item_data)
            await self._handle_knowledge_update(
                {"item": item_data},
                source,
            )

    async def _resolve_conflict(
        self,
        local: KnowledgeItem,
        remote: KnowledgeItem,
    ) -> KnowledgeItem | None:
        """
        Resolve a conflict between local and remote items.

        Returns:
            Resolved item or None if manual resolution needed
        """
        strategy = local.conflict_resolution

        if strategy == ConflictResolution.LAST_WRITE_WINS:
            return remote if remote.updated_at > local.updated_at else local

        elif strategy == ConflictResolution.FIRST_WRITE_WINS:
            return local if local.created_at < remote.created_at else remote

        elif strategy == ConflictResolution.MERGE:
            return await self._merge_items(local, remote)

        elif strategy == ConflictResolution.KEEP_BOTH:
            # Create a copy with modified key
            remote.key = f"{remote.key}:{remote.source}"
            await self._store.put(remote, notify=False)
            return local

        else:  # MANUAL
            local.sync_status = SyncStatus.CONFLICT
            return None

    async def _merge_items(
        self,
        local: KnowledgeItem,
        remote: KnowledgeItem,
    ) -> KnowledgeItem:
        """Attempt to merge two items."""
        # Simple merge strategy: for dicts, merge keys
        if isinstance(local.content, dict) and isinstance(remote.content, dict):
            merged_content = {**local.content, **remote.content}

            merged = KnowledgeItem(
                key=local.key,
                type=local.type,
                content=merged_content,
                scope=local.scope,
                version=max(local.version, remote.version) + 1,
                source=self._computer_id,
                tags=list(set(local.tags + remote.tags)),
                conflict_resolution=local.conflict_resolution,
            )
            return merged

        # For lists, concatenate
        if isinstance(local.content, list) and isinstance(remote.content, list):
            merged_content = local.content + [
                item for item in remote.content
                if item not in local.content
            ]

            merged = KnowledgeItem(
                key=local.key,
                type=local.type,
                content=merged_content,
                scope=local.scope,
                version=max(local.version, remote.version) + 1,
                source=self._computer_id,
            )
            return merged

        # Can't merge - fall back to last write wins
        return remote if remote.updated_at > local.updated_at else local

    def _on_local_change(self, item: KnowledgeItem, operation: str) -> None:
        """Handle local store change."""
        if item.scope != KnowledgeScope.LOCAL:
            self._pending_pushes.append(item.key)

    async def _sync_loop(self) -> None:
        """Background sync loop."""
        while self._running:
            try:
                await asyncio.sleep(self._sync_interval)

                if self._pending_pushes:
                    await self.sync(direction=SyncDirection.PUSH)
                    self._pending_pushes.clear()

            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"[Sync] Error in sync loop: {e}")

    def on_event(self, callback: SyncEventCallback) -> None:
        """Register callback for sync events."""
        self._event_callbacks.append(callback)

    def _emit_event(self, event: SyncEvent) -> None:
        """Emit a sync event."""
        for callback in self._event_callbacks:
            try:
                callback(event)
            except Exception:
                pass

    def get_stats(self) -> dict[str, Any]:
        """Get sync engine statistics."""
        return {
            "computer_id": self._computer_id,
            "pending_pushes": len(self._pending_pushes),
            "last_syncs": {
                computer: timestamp.isoformat()
                for computer, timestamp in self._last_sync.items()
            },
            "running": self._running,
        }
