"""
Proto Distributed Knowledge Sync Module.

Synchronizes knowledge, state, and context across multiple computers.

Usage:
    from computer_use_demo.knowledge import (
        get_knowledge_store,
        KnowledgeItem,
        KnowledgeType,
    )

    # Get the knowledge store
    store = get_knowledge_store()

    # Store knowledge
    await store.put(
        KnowledgeItem(
            key="project/readme",
            type=KnowledgeType.DOCUMENT,
            content="Project documentation...",
        )
    )

    # Retrieve knowledge
    item = await store.get("project/readme")

    # Sync with other computers
    await store.sync()
"""

from .types import (
    KnowledgeItem,
    KnowledgeType,
    KnowledgeScope,
    SyncStatus,
    ConflictResolution,
)

from .store import (
    KnowledgeStore,
    get_knowledge_store,
    shutdown_knowledge_store,
)

from .sync import (
    KnowledgeSyncEngine,
    SyncEvent,
    SyncDirection,
)

__all__ = [
    # Types
    "KnowledgeItem",
    "KnowledgeType",
    "KnowledgeScope",
    "SyncStatus",
    "ConflictResolution",
    # Store
    "KnowledgeStore",
    "get_knowledge_store",
    "shutdown_knowledge_store",
    # Sync
    "KnowledgeSyncEngine",
    "SyncEvent",
    "SyncDirection",
]
