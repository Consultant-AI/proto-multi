"""
Type definitions for the Distributed Knowledge Sync system.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any
import hashlib
import json


class KnowledgeType(str, Enum):
    """Types of knowledge items."""

    # Documents and text
    DOCUMENT = "document"
    CODE = "code"
    CONFIG = "config"

    # Structured data
    CONTEXT = "context"
    STATE = "state"
    CACHE = "cache"

    # Learned patterns
    PATTERN = "pattern"
    PREFERENCE = "preference"
    RULE = "rule"

    # Task-related
    TASK_RESULT = "task_result"
    ERROR = "error"
    LOG = "log"


class KnowledgeScope(str, Enum):
    """Visibility scope for knowledge."""

    # Only this computer
    LOCAL = "local"

    # Shared within project
    PROJECT = "project"

    # Shared globally
    GLOBAL = "global"

    # Shared with specific computers
    SELECTIVE = "selective"


class SyncStatus(str, Enum):
    """Synchronization status."""

    SYNCED = "synced"
    PENDING = "pending"
    SYNCING = "syncing"
    CONFLICT = "conflict"
    ERROR = "error"


class ConflictResolution(str, Enum):
    """Conflict resolution strategies."""

    # Latest timestamp wins
    LAST_WRITE_WINS = "last_write_wins"

    # First write is preserved
    FIRST_WRITE_WINS = "first_write_wins"

    # Merge if possible
    MERGE = "merge"

    # Manual resolution required
    MANUAL = "manual"

    # Keep both versions
    KEEP_BOTH = "keep_both"


@dataclass
class KnowledgeItem:
    """A single item of knowledge."""

    # Unique key (path-like: "project/file/section")
    key: str

    # Type of knowledge
    type: KnowledgeType = KnowledgeType.CONTEXT

    # The actual content
    content: Any = None

    # Visibility scope
    scope: KnowledgeScope = KnowledgeScope.PROJECT

    # Version number (increments on updates)
    version: int = 1

    # Content hash for conflict detection
    hash: str = ""

    # Source computer ID
    source: str | None = None

    # Computers allowed to see (for SELECTIVE scope)
    allowed_computers: list[str] = field(default_factory=list)

    # Tags for categorization
    tags: list[str] = field(default_factory=list)

    # Sync status
    sync_status: SyncStatus = SyncStatus.PENDING

    # Conflict resolution strategy
    conflict_resolution: ConflictResolution = ConflictResolution.LAST_WRITE_WINS

    # Time-to-live in seconds (0 = no expiry)
    ttl: int = 0

    # Creation timestamp
    created_at: datetime = field(default_factory=datetime.utcnow)

    # Last update timestamp
    updated_at: datetime = field(default_factory=datetime.utcnow)

    # Expiry timestamp (calculated from TTL)
    expires_at: datetime | None = None

    # Custom metadata
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Calculate hash and expiry."""
        if not self.hash:
            self.hash = self._calculate_hash()

        if self.ttl > 0 and not self.expires_at:
            from datetime import timedelta
            self.expires_at = self.created_at + timedelta(seconds=self.ttl)

    def _calculate_hash(self) -> str:
        """Calculate content hash."""
        content_str = json.dumps(self.content, sort_keys=True, default=str)
        return hashlib.sha256(content_str.encode()).hexdigest()[:16]

    def is_expired(self) -> bool:
        """Check if item has expired."""
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at

    def update_content(self, new_content: Any) -> None:
        """Update content and recalculate hash."""
        self.content = new_content
        self.version += 1
        self.hash = self._calculate_hash()
        self.updated_at = datetime.utcnow()
        self.sync_status = SyncStatus.PENDING

    def is_visible_to(self, computer_id: str) -> bool:
        """Check if item is visible to a computer."""
        if self.scope == KnowledgeScope.LOCAL:
            return self.source == computer_id
        elif self.scope == KnowledgeScope.SELECTIVE:
            return computer_id in self.allowed_computers
        return True  # PROJECT and GLOBAL are visible to all

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "key": self.key,
            "type": self.type.value,
            "content": self.content,
            "scope": self.scope.value,
            "version": self.version,
            "hash": self.hash,
            "source": self.source,
            "allowed_computers": self.allowed_computers,
            "tags": self.tags,
            "sync_status": self.sync_status.value,
            "conflict_resolution": self.conflict_resolution.value,
            "ttl": self.ttl,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "KnowledgeItem":
        """Create from dictionary."""
        item = cls(
            key=data["key"],
            type=KnowledgeType(data.get("type", "context")),
            content=data.get("content"),
            scope=KnowledgeScope(data.get("scope", "project")),
            version=data.get("version", 1),
            hash=data.get("hash", ""),
            source=data.get("source"),
            allowed_computers=data.get("allowed_computers", []),
            tags=data.get("tags", []),
            sync_status=SyncStatus(data.get("sync_status", "pending")),
            conflict_resolution=ConflictResolution(
                data.get("conflict_resolution", "last_write_wins")
            ),
            ttl=data.get("ttl", 0),
            metadata=data.get("metadata", {}),
        )

        if data.get("created_at"):
            item.created_at = datetime.fromisoformat(data["created_at"])
        if data.get("updated_at"):
            item.updated_at = datetime.fromisoformat(data["updated_at"])
        if data.get("expires_at"):
            item.expires_at = datetime.fromisoformat(data["expires_at"])

        return item


@dataclass
class KnowledgeQuery:
    """Query for searching knowledge."""

    # Key pattern (supports wildcards: "project/*")
    key_pattern: str | None = None

    # Filter by type
    types: list[KnowledgeType] | None = None

    # Filter by tags (any match)
    tags: list[str] | None = None

    # Filter by scope
    scope: KnowledgeScope | None = None

    # Filter by source computer
    source: str | None = None

    # Only include synced items
    synced_only: bool = False

    # Maximum results
    limit: int = 100

    # Offset for pagination
    offset: int = 0

    def matches(self, item: KnowledgeItem) -> bool:
        """Check if an item matches this query."""
        # Key pattern match
        if self.key_pattern:
            if not self._key_matches(item.key, self.key_pattern):
                return False

        # Type filter
        if self.types and item.type not in self.types:
            return False

        # Tags filter (any match)
        if self.tags and not any(t in item.tags for t in self.tags):
            return False

        # Scope filter
        if self.scope and item.scope != self.scope:
            return False

        # Source filter
        if self.source and item.source != self.source:
            return False

        # Synced filter
        if self.synced_only and item.sync_status != SyncStatus.SYNCED:
            return False

        return True

    def _key_matches(self, key: str, pattern: str) -> bool:
        """Check if key matches pattern with wildcards."""
        import fnmatch
        return fnmatch.fnmatch(key, pattern)
