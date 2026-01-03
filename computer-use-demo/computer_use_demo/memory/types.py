"""
Type definitions for the memory system.
"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


class MemoryLevel(str, Enum):
    """Memory hierarchy levels from highest to lowest priority."""

    DIRECTORY = "directory"   # Most specific - .claude/CLAUDE.md in current dir
    PROJECT = "project"       # Project level - .claude/CLAUDE.md at project root
    ENTERPRISE = "enterprise" # Global - ~/.claude/CLAUDE.md


@dataclass
class MemorySection:
    """A section within a CLAUDE.md file."""

    # Section title (from markdown header)
    title: str

    # Section content (markdown)
    content: str

    # Header level (1-6)
    level: int = 2

    # Tags/metadata parsed from content
    tags: list[str] = field(default_factory=list)


@dataclass
class MemoryFile:
    """Represents a single CLAUDE.md file."""

    # Path to the file
    path: Path

    # Memory level
    level: MemoryLevel

    # Parsed sections
    sections: list[MemorySection] = field(default_factory=list)

    # Raw content
    raw_content: str = ""

    # Whether file exists
    exists: bool = False

    # Last modified time
    modified_at: float | None = None


@dataclass
class MergedMemory:
    """Result of merging memory from multiple levels."""

    # Merged sections (later levels override earlier)
    sections: dict[str, MemorySection] = field(default_factory=dict)

    # Source files that contributed
    sources: list[MemoryFile] = field(default_factory=list)

    # Full merged content
    content: str = ""

    # Metadata about the merge
    metadata: dict[str, Any] = field(default_factory=dict)

    def get_section(self, title: str) -> MemorySection | None:
        """Get a specific section by title."""
        return self.sections.get(title.lower())

    def has_section(self, title: str) -> bool:
        """Check if a section exists."""
        return title.lower() in self.sections
