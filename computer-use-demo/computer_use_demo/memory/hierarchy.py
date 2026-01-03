"""
Memory hierarchy management.

Handles merging of CLAUDE.md files from different levels:
- Enterprise (global): ~/.claude/CLAUDE.md
- Project: .claude/CLAUDE.md at project root
- Directory: .claude/CLAUDE.md in current directory
"""

import os
from pathlib import Path

from .claude_md import parse_claude_md
from .types import MemoryFile, MemoryLevel, MemorySection, MergedMemory


def get_enterprise_memory_path() -> Path:
    """Get path to enterprise-level CLAUDE.md."""
    return Path.home() / ".claude" / "CLAUDE.md"


def get_project_memory_path(project_root: Path | None = None) -> Path | None:
    """
    Get path to project-level CLAUDE.md.

    Searches upward from current directory for a project root
    (directory containing .git, .claude, package.json, etc.)
    """
    if project_root:
        return project_root / ".claude" / "CLAUDE.md"

    # Search upward for project root
    current = Path.cwd()

    # Project indicators
    indicators = [".git", ".claude", "package.json", "pyproject.toml", "Cargo.toml", ".project_root"]

    while current != current.parent:
        for indicator in indicators:
            if (current / indicator).exists():
                return current / ".claude" / "CLAUDE.md"
        current = current.parent

    return None


def get_directory_memory_path(directory: Path | None = None) -> Path:
    """Get path to directory-level CLAUDE.md."""
    directory = directory or Path.cwd()
    return directory / ".claude" / "CLAUDE.md"


def load_memory_hierarchy(
    project_root: Path | None = None,
    directory: Path | None = None,
) -> MergedMemory:
    """
    Load and merge memory from all levels.

    Order of precedence (later overrides earlier):
    1. Enterprise (lowest priority)
    2. Project
    3. Directory (highest priority)

    Args:
        project_root: Optional explicit project root path
        directory: Optional directory for directory-level memory

    Returns:
        MergedMemory with all sections merged
    """
    sources: list[MemoryFile] = []

    # Load enterprise memory
    enterprise_path = get_enterprise_memory_path()
    enterprise = parse_claude_md(enterprise_path, MemoryLevel.ENTERPRISE)
    if enterprise.exists:
        sources.append(enterprise)

    # Load project memory
    project_path = get_project_memory_path(project_root)
    if project_path:
        project = parse_claude_md(project_path, MemoryLevel.PROJECT)
        if project.exists:
            sources.append(project)

    # Load directory memory
    dir_path = get_directory_memory_path(directory)
    # Only load if different from project path
    if not project_path or dir_path != project_path:
        dir_memory = parse_claude_md(dir_path, MemoryLevel.DIRECTORY)
        if dir_memory.exists:
            sources.append(dir_memory)

    return merge_memories(sources)


def merge_memories(sources: list[MemoryFile]) -> MergedMemory:
    """
    Merge multiple memory files into one.

    Later sources override earlier sources (same section title replaces).
    """
    merged_sections: dict[str, MemorySection] = {}

    for source in sources:
        for section in source.sections:
            # Use lowercase title as key for case-insensitive matching
            key = section.title.lower()
            merged_sections[key] = section

    # Build merged content
    content_parts = []
    for section in merged_sections.values():
        if section.level > 0:
            header = "#" * section.level
            content_parts.append(f"{header} {section.title}\n\n{section.content}")
        else:
            content_parts.append(section.content)

    return MergedMemory(
        sections=merged_sections,
        sources=sources,
        content="\n\n".join(content_parts),
        metadata={
            "source_count": len(sources),
            "section_count": len(merged_sections),
            "levels": [s.level.value for s in sources],
        },
    )


def get_memory_for_injection(merged: MergedMemory) -> str:
    """
    Format merged memory for injection into agent context.

    Returns formatted content suitable for system prompt injection.
    """
    if not merged.content:
        return ""

    return f"""<MEMORY>
The following are conventions, patterns, and context from CLAUDE.md files:

{merged.content}
</MEMORY>"""
