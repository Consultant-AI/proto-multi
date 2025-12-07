"""
Knowledge Management System for Project Context.

This module provides knowledge storage and retrieval capabilities for projects,
enabling agents to persist learnings, decisions, patterns, and context across
executions.
"""

import json
import uuid
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Optional


class KnowledgeType(str, Enum):
    """Knowledge entry type enumeration."""

    TECHNICAL_DECISION = "technical_decision"
    LEARNING = "learning"
    PATTERN = "pattern"
    REFERENCE = "reference"
    CONTEXT = "context"
    BEST_PRACTICE = "best_practice"
    LESSON_LEARNED = "lesson_learned"


class KnowledgeEntry:
    """Represents a knowledge base entry."""

    def __init__(
        self,
        title: str,
        content: str,
        knowledge_type: KnowledgeType = KnowledgeType.CONTEXT,
        tags: Optional[list[str]] = None,
        source: Optional[str] = None,
        entry_id: Optional[str] = None,
        created_at: Optional[str] = None,
        updated_at: Optional[str] = None,
        relevance_score: float = 1.0,
        metadata: Optional[dict[str, Any]] = None,
        related_tasks: Optional[list[str]] = None,
        related_entries: Optional[list[str]] = None,
    ):
        """
        Initialize a knowledge entry.

        Args:
            title: Entry title/summary
            content: Detailed knowledge content
            knowledge_type: Type of knowledge
            tags: List of tags for categorization
            source: Source of knowledge (agent name, document, etc.)
            entry_id: Unique entry identifier (auto-generated if not provided)
            created_at: ISO timestamp when entry was created
            updated_at: ISO timestamp when entry was last updated
            relevance_score: Relevance score (0.0-1.0)
            metadata: Additional metadata dictionary
            related_tasks: List of related task IDs
            related_entries: List of related knowledge entry IDs
        """
        self.id = entry_id or str(uuid.uuid4())
        self.title = title
        self.content = content
        self.type = KnowledgeType(knowledge_type) if isinstance(knowledge_type, str) else knowledge_type
        self.tags = tags or []
        self.source = source
        self.created_at = created_at or datetime.utcnow().isoformat()
        self.updated_at = updated_at or self.created_at
        self.relevance_score = relevance_score
        self.metadata = metadata or {}
        self.related_tasks = related_tasks or []
        self.related_entries = related_entries or []

    def to_dict(self) -> dict[str, Any]:
        """Convert entry to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "type": self.type.value,
            "tags": self.tags,
            "source": self.source,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "relevance_score": self.relevance_score,
            "metadata": self.metadata,
            "related_tasks": self.related_tasks,
            "related_entries": self.related_entries,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "KnowledgeEntry":
        """Create entry from dictionary."""
        return cls(
            entry_id=data["id"],
            title=data["title"],
            content=data["content"],
            knowledge_type=data.get("type", KnowledgeType.CONTEXT),
            tags=data.get("tags", []),
            source=data.get("source"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            relevance_score=data.get("relevance_score", 1.0),
            metadata=data.get("metadata", {}),
            related_tasks=data.get("related_tasks", []),
            related_entries=data.get("related_entries", []),
        )

    def update_content(self, content: str) -> None:
        """Update entry content with timestamp."""
        self.content = content
        self.updated_at = datetime.utcnow().isoformat()

    def add_tag(self, tag: str) -> None:
        """Add tag if not already present."""
        if tag not in self.tags:
            self.tags.append(tag)
            self.updated_at = datetime.utcnow().isoformat()

    def add_related_task(self, task_id: str) -> None:
        """Link entry to a task."""
        if task_id not in self.related_tasks:
            self.related_tasks.append(task_id)
            self.updated_at = datetime.utcnow().isoformat()

    def add_related_entry(self, entry_id: str) -> None:
        """Link entry to another knowledge entry."""
        if entry_id not in self.related_entries:
            self.related_entries.append(entry_id)
            self.updated_at = datetime.utcnow().isoformat()

    def __repr__(self) -> str:
        """String representation of entry."""
        return f"KnowledgeEntry(id={self.id[:8]}, title={self.title}, type={self.type.value})"


class KnowledgeStore:
    """Manages knowledge base for a project."""

    def __init__(self, project_path: Path):
        """
        Initialize knowledge store for a project.

        Args:
            project_path: Path to project directory
        """
        self.project_path = Path(project_path)
        self.knowledge_dir = self.project_path / "knowledge"
        self.index_file = self.knowledge_dir / "index.json"
        self.entries: dict[str, KnowledgeEntry] = {}
        self._ensure_directories()
        self._load_index()

    def _ensure_directories(self) -> None:
        """Create knowledge directory structure."""
        subdirs = ["technical", "context", "learnings", "patterns", "references"]
        for subdir in subdirs:
            (self.knowledge_dir / subdir).mkdir(parents=True, exist_ok=True)

    def _get_entry_path(self, entry: KnowledgeEntry) -> Path:
        """Get file path for knowledge entry."""
        # Organize by type
        type_dir_map = {
            KnowledgeType.TECHNICAL_DECISION: "technical",
            KnowledgeType.LEARNING: "learnings",
            KnowledgeType.LESSON_LEARNED: "learnings",
            KnowledgeType.PATTERN: "patterns",
            KnowledgeType.BEST_PRACTICE: "patterns",
            KnowledgeType.REFERENCE: "references",
            KnowledgeType.CONTEXT: "context",
        }
        subdir = type_dir_map.get(entry.type, "context")
        return self.knowledge_dir / subdir / f"{entry.id}.json"

    def _load_index(self) -> None:
        """Load knowledge index from disk."""
        if self.index_file.exists():
            try:
                with open(self.index_file, "r") as f:
                    data = json.load(f)
                    entry_ids = data.get("entries", [])

                    # Load each entry
                    for entry_id in entry_ids:
                        entry_data = data.get("entry_data", {}).get(entry_id)
                        if entry_data:
                            entry = KnowledgeEntry.from_dict(entry_data)
                            self.entries[entry_id] = entry
            except Exception as e:
                print(f"Warning: Failed to load knowledge index: {e}")
                self.entries = {}
        else:
            self.entries = {}

    def _save_index(self) -> None:
        """Save knowledge index to disk."""
        self.knowledge_dir.mkdir(parents=True, exist_ok=True)
        data = {
            "version": "1.0",
            "updated_at": datetime.utcnow().isoformat(),
            "entries": list(self.entries.keys()),
            "entry_data": {entry_id: entry.to_dict() for entry_id, entry in self.entries.items()},
        }
        with open(self.index_file, "w") as f:
            json.dump(data, f, indent=2)

    def _save_entry(self, entry: KnowledgeEntry) -> None:
        """Save individual entry to its own file."""
        entry_path = self._get_entry_path(entry)
        entry_path.parent.mkdir(parents=True, exist_ok=True)
        with open(entry_path, "w") as f:
            json.dump(entry.to_dict(), f, indent=2)

    def add_entry(
        self,
        title: str,
        content: str,
        knowledge_type: KnowledgeType = KnowledgeType.CONTEXT,
        tags: Optional[list[str]] = None,
        source: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
        related_tasks: Optional[list[str]] = None,
    ) -> KnowledgeEntry:
        """
        Add new knowledge entry.

        Args:
            title: Entry title
            content: Entry content
            knowledge_type: Type of knowledge
            tags: Tags for categorization
            source: Source of knowledge
            metadata: Additional metadata
            related_tasks: Related task IDs

        Returns:
            Created knowledge entry
        """
        entry = KnowledgeEntry(
            title=title,
            content=content,
            knowledge_type=knowledge_type,
            tags=tags,
            source=source,
            metadata=metadata,
            related_tasks=related_tasks,
        )
        self.entries[entry.id] = entry
        self._save_entry(entry)
        self._save_index()
        return entry

    def get_entry(self, entry_id: str) -> Optional[KnowledgeEntry]:
        """Get entry by ID."""
        return self.entries.get(entry_id)

    def get_all_entries(self) -> list[KnowledgeEntry]:
        """Get all knowledge entries."""
        return list(self.entries.values())

    def get_entries_by_type(self, knowledge_type: KnowledgeType) -> list[KnowledgeEntry]:
        """Get entries of specific type."""
        return [entry for entry in self.entries.values() if entry.type == knowledge_type]

    def get_entries_by_tag(self, tag: str) -> list[KnowledgeEntry]:
        """Get entries with specific tag."""
        return [entry for entry in self.entries.values() if tag in entry.tags]

    def get_entries_by_source(self, source: str) -> list[KnowledgeEntry]:
        """Get entries from specific source."""
        return [entry for entry in self.entries.values() if entry.source == source]

    def search_entries(self, query: str, case_sensitive: bool = False) -> list[KnowledgeEntry]:
        """
        Search entries by keyword in title or content.

        Args:
            query: Search query
            case_sensitive: Whether search is case-sensitive

        Returns:
            List of matching entries, sorted by relevance
        """
        query_str = query if case_sensitive else query.lower()
        results = []

        for entry in self.entries.values():
            title = entry.title if case_sensitive else entry.title.lower()
            content = entry.content if case_sensitive else entry.content.lower()

            # Simple keyword matching with scoring
            score = 0.0
            if query_str in title:
                score += 2.0  # Title matches are more relevant
            if query_str in content:
                score += 1.0

            # Check tags
            for tag in entry.tags:
                tag_str = tag if case_sensitive else tag.lower()
                if query_str in tag_str:
                    score += 1.5

            if score > 0:
                # Adjust by entry's relevance score
                final_score = score * entry.relevance_score
                results.append((entry, final_score))

        # Sort by score (descending)
        results.sort(key=lambda x: x[1], reverse=True)
        return [entry for entry, _ in results]

    def update_entry(
        self,
        entry_id: str,
        title: Optional[str] = None,
        content: Optional[str] = None,
        add_tags: Optional[list[str]] = None,
        remove_tags: Optional[list[str]] = None,
        relevance_score: Optional[float] = None,
    ) -> Optional[KnowledgeEntry]:
        """
        Update knowledge entry.

        Args:
            entry_id: ID of entry to update
            title: New title
            content: New content
            add_tags: Tags to add
            remove_tags: Tags to remove
            relevance_score: New relevance score

        Returns:
            Updated entry or None if not found
        """
        entry = self.get_entry(entry_id)
        if not entry:
            return None

        if title is not None:
            entry.title = title
        if content is not None:
            entry.update_content(content)
        if add_tags:
            for tag in add_tags:
                entry.add_tag(tag)
        if remove_tags:
            entry.tags = [tag for tag in entry.tags if tag not in remove_tags]
        if relevance_score is not None:
            entry.relevance_score = max(0.0, min(1.0, relevance_score))

        entry.updated_at = datetime.utcnow().isoformat()
        self._save_entry(entry)
        self._save_index()
        return entry

    def link_to_task(self, entry_id: str, task_id: str) -> bool:
        """Link knowledge entry to a task."""
        entry = self.get_entry(entry_id)
        if entry:
            entry.add_related_task(task_id)
            self._save_entry(entry)
            self._save_index()
            return True
        return False

    def link_entries(self, entry_id1: str, entry_id2: str) -> bool:
        """Create bidirectional link between two entries."""
        entry1 = self.get_entry(entry_id1)
        entry2 = self.get_entry(entry_id2)

        if entry1 and entry2:
            entry1.add_related_entry(entry_id2)
            entry2.add_related_entry(entry_id1)
            self._save_entry(entry1)
            self._save_entry(entry2)
            self._save_index()
            return True
        return False

    def get_related_entries(self, entry_id: str) -> list[KnowledgeEntry]:
        """Get entries related to a specific entry."""
        entry = self.get_entry(entry_id)
        if not entry:
            return []

        return [
            self.entries[related_id]
            for related_id in entry.related_entries
            if related_id in self.entries
        ]

    def get_entries_for_task(self, task_id: str) -> list[KnowledgeEntry]:
        """Get all knowledge entries related to a task."""
        return [
            entry for entry in self.entries.values()
            if task_id in entry.related_tasks
        ]

    def get_knowledge_summary(self) -> dict[str, Any]:
        """Get summary statistics of knowledge base."""
        all_entries = self.get_all_entries()
        return {
            "total": len(all_entries),
            "by_type": {
                "technical_decisions": len(self.get_entries_by_type(KnowledgeType.TECHNICAL_DECISION)),
                "learnings": len(self.get_entries_by_type(KnowledgeType.LEARNING)),
                "patterns": len(self.get_entries_by_type(KnowledgeType.PATTERN)),
                "references": len(self.get_entries_by_type(KnowledgeType.REFERENCE)),
                "context": len(self.get_entries_by_type(KnowledgeType.CONTEXT)),
                "best_practices": len(self.get_entries_by_type(KnowledgeType.BEST_PRACTICE)),
                "lessons_learned": len(self.get_entries_by_type(KnowledgeType.LESSON_LEARNED)),
            },
            "avg_relevance": (
                sum(e.relevance_score for e in all_entries) / len(all_entries)
                if all_entries else 0.0
            ),
        }
