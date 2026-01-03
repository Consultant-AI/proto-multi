"""
Proto Memory Module - CLAUDE.md hierarchy management.

Provides persistent conventions and patterns across sessions through
a hierarchical CLAUDE.md memory system.

Memory Hierarchy (later overrides earlier):
1. Enterprise: ~/.claude/CLAUDE.md (global settings)
2. Project: .claude/CLAUDE.md (project-specific)
3. Directory: .claude/CLAUDE.md (directory-specific)

Usage:
    from computer_use_demo.memory import (
        load_memory,
        get_memory_injection,
        get_memory_loader,
    )

    # Load merged memory from hierarchy
    memory = load_memory()
    print(f"Loaded {memory.metadata['section_count']} sections")

    # Get formatted content for agent injection
    injection = get_memory_injection()
    # Use injection in system prompt

    # Use loader for caching
    loader = get_memory_loader()
    memory = loader.load()  # Uses cache if available
"""

from .claude_md import (
    format_memory_file,
    format_section,
    parse_claude_md,
)

from .hierarchy import (
    get_directory_memory_path,
    get_enterprise_memory_path,
    get_memory_for_injection,
    get_project_memory_path,
    load_memory_hierarchy,
    merge_memories,
)

from .loader import (
    MemoryLoader,
    get_memory_injection,
    get_memory_loader,
    load_memory,
)

from .types import (
    MemoryFile,
    MemoryLevel,
    MemorySection,
    MergedMemory,
)

__all__ = [
    # Types
    "MemoryFile",
    "MemoryLevel",
    "MemorySection",
    "MergedMemory",
    # Parser
    "parse_claude_md",
    "format_section",
    "format_memory_file",
    # Hierarchy
    "get_enterprise_memory_path",
    "get_project_memory_path",
    "get_directory_memory_path",
    "load_memory_hierarchy",
    "merge_memories",
    "get_memory_for_injection",
    # Loader
    "MemoryLoader",
    "get_memory_loader",
    "load_memory",
    "get_memory_injection",
]
