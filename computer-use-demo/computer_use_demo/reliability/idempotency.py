"""
Idempotency key management for safe retries.

Ensures external operations can be safely retried without duplicate effects.
"""

import hashlib
import json
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class IdempotencyRecord:
    """Record of an idempotent operation."""

    key: str
    operation: str
    created_at: float
    completed_at: float | None = None
    result: Any = None
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def is_complete(self) -> bool:
        """Check if operation has completed."""
        return self.completed_at is not None

    @property
    def is_success(self) -> bool:
        """Check if operation completed successfully."""
        return self.is_complete and self.error is None


class IdempotencyManager:
    """
    Manages idempotency keys for external operations.

    Prevents duplicate operations when retrying after failures.
    Keys are stored in memory and optionally persisted to disk.
    """

    def __init__(self, storage_path: str | Path | None = None, ttl_hours: float = 24.0):
        """
        Initialize idempotency manager.

        Args:
            storage_path: Path for persistent storage. None = memory only.
            ttl_hours: Time-to-live for keys in hours.
        """
        self._records: dict[str, IdempotencyRecord] = {}
        self._storage_path = Path(storage_path) if storage_path else None
        self._ttl_seconds = ttl_hours * 3600

        if self._storage_path:
            self._storage_path.mkdir(parents=True, exist_ok=True)
            self._load_from_disk()

    def generate_key(
        self,
        operation: str,
        *args,
        **kwargs,
    ) -> str:
        """
        Generate a deterministic idempotency key.

        The key is based on the operation and its arguments,
        so the same call always generates the same key.

        Args:
            operation: Name of the operation
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Unique idempotency key
        """
        # Create deterministic hash of operation + args
        data = {
            "operation": operation,
            "args": args,
            "kwargs": kwargs,
        }
        data_str = json.dumps(data, sort_keys=True, default=str)
        hash_value = hashlib.sha256(data_str.encode()).hexdigest()[:16]

        return f"{operation}:{hash_value}"

    def generate_unique_key(self, prefix: str = "") -> str:
        """
        Generate a unique idempotency key.

        Use this when you need a new key each time (not deterministic).

        Args:
            prefix: Optional prefix for the key

        Returns:
            Unique key
        """
        unique_id = str(uuid.uuid4())[:8]
        timestamp = int(time.time() * 1000) % 1000000
        if prefix:
            return f"{prefix}:{timestamp}:{unique_id}"
        return f"{timestamp}:{unique_id}"

    def check_key(self, key: str) -> IdempotencyRecord | None:
        """
        Check if an idempotency key has been used.

        Args:
            key: Idempotency key to check

        Returns:
            IdempotencyRecord if key exists, None otherwise
        """
        record = self._records.get(key)

        if record:
            # Check if expired
            age = time.time() - record.created_at
            if age > self._ttl_seconds:
                del self._records[key]
                return None

        return record

    def start_operation(
        self,
        key: str,
        operation: str,
        metadata: dict[str, Any] | None = None,
    ) -> IdempotencyRecord:
        """
        Start tracking an operation with an idempotency key.

        Args:
            key: Idempotency key
            operation: Operation name
            metadata: Additional metadata

        Returns:
            New IdempotencyRecord

        Raises:
            ValueError: If key is already in use
        """
        existing = self.check_key(key)
        if existing:
            if existing.is_complete:
                # Return the existing result
                return existing
            else:
                # Operation in progress - this is a duplicate
                raise ValueError(f"Operation with key {key} is already in progress")

        record = IdempotencyRecord(
            key=key,
            operation=operation,
            created_at=time.time(),
            metadata=metadata or {},
        )

        self._records[key] = record
        self._save_to_disk()

        return record

    def complete_operation(
        self,
        key: str,
        result: Any = None,
        error: str | None = None,
    ) -> IdempotencyRecord | None:
        """
        Mark an operation as complete.

        Args:
            key: Idempotency key
            result: Operation result (if successful)
            error: Error message (if failed)

        Returns:
            Updated IdempotencyRecord or None if not found
        """
        record = self._records.get(key)
        if not record:
            return None

        record.completed_at = time.time()
        record.result = result
        record.error = error

        self._save_to_disk()

        return record

    def get_or_execute(
        self,
        key: str,
        operation: str,
        execute_fn: callable,
        metadata: dict[str, Any] | None = None,
    ) -> tuple[Any, bool]:
        """
        Get cached result or execute operation.

        Args:
            key: Idempotency key
            operation: Operation name
            execute_fn: Function to execute if not cached
            metadata: Additional metadata

        Returns:
            Tuple of (result, was_cached)
        """
        # Check for existing result
        existing = self.check_key(key)
        if existing and existing.is_complete:
            if existing.error:
                raise Exception(existing.error)
            return existing.result, True

        # Start new operation
        try:
            self.start_operation(key, operation, metadata)
        except ValueError:
            # Already in progress - wait and check again
            existing = self.check_key(key)
            if existing and existing.is_complete:
                if existing.error:
                    raise Exception(existing.error)
                return existing.result, True
            raise

        # Execute the operation
        try:
            result = execute_fn()
            self.complete_operation(key, result=result)
            return result, False
        except Exception as e:
            self.complete_operation(key, error=str(e))
            raise

    def cleanup_expired(self) -> int:
        """
        Remove expired idempotency records.

        Returns:
            Number of records removed
        """
        now = time.time()
        expired_keys = [
            key for key, record in self._records.items()
            if (now - record.created_at) > self._ttl_seconds
        ]

        for key in expired_keys:
            del self._records[key]

        if expired_keys:
            self._save_to_disk()

        return len(expired_keys)

    def _save_to_disk(self) -> None:
        """Save records to disk if storage path is set."""
        if not self._storage_path:
            return

        try:
            records_file = self._storage_path / "idempotency_records.json"
            data = {
                key: {
                    "key": r.key,
                    "operation": r.operation,
                    "created_at": r.created_at,
                    "completed_at": r.completed_at,
                    "result": r.result,
                    "error": r.error,
                    "metadata": r.metadata,
                }
                for key, r in self._records.items()
            }
            with open(records_file, "w") as f:
                json.dump(data, f, default=str)
        except Exception as e:
            print(f"[Idempotency] Failed to save records: {e}")

    def _load_from_disk(self) -> None:
        """Load records from disk if available."""
        if not self._storage_path:
            return

        records_file = self._storage_path / "idempotency_records.json"
        if not records_file.exists():
            return

        try:
            with open(records_file, "r") as f:
                data = json.load(f)

            for key, record_data in data.items():
                self._records[key] = IdempotencyRecord(
                    key=record_data["key"],
                    operation=record_data["operation"],
                    created_at=record_data["created_at"],
                    completed_at=record_data.get("completed_at"),
                    result=record_data.get("result"),
                    error=record_data.get("error"),
                    metadata=record_data.get("metadata", {}),
                )
        except Exception as e:
            print(f"[Idempotency] Failed to load records: {e}")


# Global idempotency manager
_idempotency_manager: IdempotencyManager | None = None


def get_idempotency_manager() -> IdempotencyManager:
    """Get the global idempotency manager instance."""
    global _idempotency_manager
    if _idempotency_manager is None:
        storage_path = Path.home() / ".proto" / "idempotency"
        _idempotency_manager = IdempotencyManager(storage_path=storage_path)
    return _idempotency_manager
