"""
Knowledge Store implementation.

Local storage for knowledge items with sync support.
"""

import asyncio
import json
import threading
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

from .types import (
    KnowledgeItem,
    KnowledgeQuery,
    KnowledgeScope,
    KnowledgeType,
    SyncStatus,
)


# Type for change callbacks
ChangeCallback = Callable[[KnowledgeItem, str], None]  # item, operation


class KnowledgeStore:
    """
    Local knowledge store with persistence and sync support.

    Features:
    - Key-value storage with hierarchical keys
    - Type-based organization
    - TTL and expiry
    - Change tracking for sync
    - Query support
    """

    def __init__(
        self,
        data_dir: Path | None = None,
        computer_id: str = "local",
        auto_save: bool = True,
        save_interval: float = 30.0,
    ):
        self._data_dir = data_dir or Path.home() / ".proto" / "knowledge"
        self._computer_id = computer_id
        self._auto_save = auto_save
        self._save_interval = save_interval

        self._data_dir.mkdir(parents=True, exist_ok=True)

        # Storage
        self._items: dict[str, KnowledgeItem] = {}
        self._lock = threading.Lock()

        # Change tracking
        self._pending_changes: list[tuple[str, str]] = []  # (key, operation)
        self._change_callbacks: list[ChangeCallback] = []

        # Background tasks
        self._running = False
        self._save_task: asyncio.Task | None = None
        self._cleanup_task: asyncio.Task | None = None

        # Load persisted data
        self._load()

    def _load(self) -> None:
        """Load knowledge from disk."""
        data_file = self._data_dir / "knowledge.json"
        if data_file.exists():
            try:
                with open(data_file, "r") as f:
                    data = json.load(f)

                for item_data in data.get("items", []):
                    item = KnowledgeItem.from_dict(item_data)
                    if not item.is_expired():
                        self._items[item.key] = item

                print(f"[Knowledge] Loaded {len(self._items)} items")

            except Exception as e:
                print(f"[Knowledge] Failed to load: {e}")

    def _save(self) -> None:
        """Save knowledge to disk."""
        data_file = self._data_dir / "knowledge.json"
        data = {
            "items": [item.to_dict() for item in self._items.values()],
            "updated_at": datetime.utcnow().isoformat(),
        }

        with open(data_file, "w") as f:
            json.dump(data, f, indent=2)

    async def start(self) -> None:
        """Start background tasks."""
        self._running = True

        if self._auto_save:
            self._save_task = asyncio.create_task(self._auto_save_loop())

        self._cleanup_task = asyncio.create_task(self._cleanup_loop())

        print("[Knowledge] Store started")

    async def stop(self) -> None:
        """Stop background tasks and save."""
        self._running = False

        if self._save_task:
            self._save_task.cancel()
            try:
                await self._save_task
            except asyncio.CancelledError:
                pass

        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass

        self._save()
        print("[Knowledge] Store stopped")

    async def put(
        self,
        item: KnowledgeItem,
        notify: bool = True,
    ) -> None:
        """
        Store a knowledge item.

        Args:
            item: Item to store
            notify: Whether to notify callbacks
        """
        with self._lock:
            # Set source if not set
            if not item.source:
                item.source = self._computer_id

            # Check for existing item
            existing = self._items.get(item.key)
            operation = "update" if existing else "create"

            # Store item
            self._items[item.key] = item

            # Track change
            self._pending_changes.append((item.key, operation))

        # Notify callbacks
        if notify:
            for callback in self._change_callbacks:
                try:
                    callback(item, operation)
                except Exception:
                    pass

    async def get(self, key: str) -> KnowledgeItem | None:
        """Get a knowledge item by key."""
        with self._lock:
            item = self._items.get(key)

            if item and item.is_expired():
                del self._items[key]
                return None

            return item

    async def delete(self, key: str, notify: bool = True) -> bool:
        """Delete a knowledge item."""
        with self._lock:
            item = self._items.pop(key, None)
            if item:
                self._pending_changes.append((key, "delete"))

        if item and notify:
            for callback in self._change_callbacks:
                try:
                    callback(item, "delete")
                except Exception:
                    pass

        return item is not None

    async def exists(self, key: str) -> bool:
        """Check if a key exists."""
        with self._lock:
            item = self._items.get(key)
            if item and item.is_expired():
                del self._items[key]
                return False
            return item is not None

    async def query(self, q: KnowledgeQuery) -> list[KnowledgeItem]:
        """Query knowledge items."""
        with self._lock:
            results = []

            for item in self._items.values():
                if item.is_expired():
                    continue

                if q.matches(item):
                    results.append(item)

            # Sort by updated_at descending
            results.sort(key=lambda x: x.updated_at, reverse=True)

            # Apply pagination
            if q.offset:
                results = results[q.offset:]
            if q.limit:
                results = results[:q.limit]

            return results

    async def list_keys(self, prefix: str | None = None) -> list[str]:
        """List all keys, optionally filtered by prefix."""
        with self._lock:
            keys = list(self._items.keys())

            if prefix:
                keys = [k for k in keys if k.startswith(prefix)]

            return sorted(keys)

    async def list_by_type(self, knowledge_type: KnowledgeType) -> list[KnowledgeItem]:
        """List items of a specific type."""
        query = KnowledgeQuery(types=[knowledge_type])
        return await self.query(query)

    async def list_by_tags(self, tags: list[str]) -> list[KnowledgeItem]:
        """List items with any of the specified tags."""
        query = KnowledgeQuery(tags=tags)
        return await self.query(query)

    async def get_pending_sync(self) -> list[KnowledgeItem]:
        """Get items pending synchronization."""
        query = KnowledgeQuery(synced_only=False)
        results = await self.query(query)
        return [
            item for item in results
            if item.sync_status == SyncStatus.PENDING
            and item.scope != KnowledgeScope.LOCAL
        ]

    async def mark_synced(self, keys: list[str]) -> None:
        """Mark items as synced."""
        with self._lock:
            for key in keys:
                if key in self._items:
                    self._items[key].sync_status = SyncStatus.SYNCED

    async def get_changes_since(
        self,
        since: datetime,
    ) -> list[KnowledgeItem]:
        """Get items changed since a timestamp."""
        with self._lock:
            return [
                item for item in self._items.values()
                if item.updated_at > since
                and item.scope != KnowledgeScope.LOCAL
            ]

    def get_pending_changes(self) -> list[tuple[str, str]]:
        """Get and clear pending changes."""
        with self._lock:
            changes = self._pending_changes.copy()
            self._pending_changes.clear()
            return changes

    def on_change(self, callback: ChangeCallback) -> None:
        """Register callback for changes."""
        self._change_callbacks.append(callback)

    async def _auto_save_loop(self) -> None:
        """Background loop for auto-saving."""
        while self._running:
            try:
                await asyncio.sleep(self._save_interval)
                with self._lock:
                    self._save()
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"[Knowledge] Auto-save error: {e}")

    async def _cleanup_loop(self) -> None:
        """Background loop for cleaning expired items."""
        while self._running:
            try:
                await asyncio.sleep(60)  # Check every minute

                with self._lock:
                    expired = [
                        key for key, item in self._items.items()
                        if item.is_expired()
                    ]

                    for key in expired:
                        del self._items[key]

                    if expired:
                        print(f"[Knowledge] Cleaned up {len(expired)} expired items")

            except asyncio.CancelledError:
                break
            except Exception:
                pass

    def get_stats(self) -> dict[str, Any]:
        """Get store statistics."""
        with self._lock:
            items = list(self._items.values())

            by_type = {}
            for t in KnowledgeType:
                count = sum(1 for i in items if i.type == t)
                if count > 0:
                    by_type[t.value] = count

            by_scope = {}
            for s in KnowledgeScope:
                count = sum(1 for i in items if i.scope == s)
                if count > 0:
                    by_scope[s.value] = count

            pending = sum(1 for i in items if i.sync_status == SyncStatus.PENDING)

            return {
                "total_items": len(items),
                "by_type": by_type,
                "by_scope": by_scope,
                "pending_sync": pending,
                "pending_changes": len(self._pending_changes),
            }


# Global store instance
_global_store: KnowledgeStore | None = None


def get_knowledge_store() -> KnowledgeStore:
    """Get or create the global knowledge store."""
    global _global_store

    if _global_store is None:
        _global_store = KnowledgeStore()

    return _global_store


async def shutdown_knowledge_store() -> None:
    """Shutdown the global knowledge store."""
    global _global_store

    if _global_store:
        await _global_store.stop()
        _global_store = None
