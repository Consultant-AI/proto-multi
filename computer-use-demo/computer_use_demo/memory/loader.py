"""
Memory loader for auto-loading CLAUDE.md on session start.

Provides convenient functions for loading and caching memory.
"""

import threading
import time
from pathlib import Path
from typing import Any

from .hierarchy import get_memory_for_injection, load_memory_hierarchy
from .types import MergedMemory


class MemoryLoader:
    """
    Loads and caches memory from CLAUDE.md hierarchy.

    Features:
    - Lazy loading
    - Caching with TTL
    - Thread-safe
    - Auto-reload on file changes
    """

    def __init__(
        self,
        project_root: Path | None = None,
        directory: Path | None = None,
        cache_ttl: float = 60.0,  # Cache for 60 seconds
    ):
        self._project_root = project_root
        self._directory = directory
        self._cache_ttl = cache_ttl

        self._cached_memory: MergedMemory | None = None
        self._cache_time: float = 0.0
        self._lock = threading.Lock()

    def load(self, force_refresh: bool = False) -> MergedMemory:
        """
        Load memory from hierarchy.

        Uses cached version if available and not expired.

        Args:
            force_refresh: If True, bypass cache

        Returns:
            MergedMemory
        """
        with self._lock:
            now = time.time()

            # Check cache
            if not force_refresh and self._cached_memory is not None:
                if now - self._cache_time < self._cache_ttl:
                    return self._cached_memory

            # Load fresh
            self._cached_memory = load_memory_hierarchy(
                project_root=self._project_root,
                directory=self._directory,
            )
            self._cache_time = now

            return self._cached_memory

    def get_injection_content(self, force_refresh: bool = False) -> str:
        """
        Get formatted content for injection into agent context.

        Args:
            force_refresh: If True, bypass cache

        Returns:
            Formatted string for system prompt injection
        """
        memory = self.load(force_refresh)
        return get_memory_for_injection(memory)

    def invalidate_cache(self) -> None:
        """Invalidate the cache, forcing reload on next access."""
        with self._lock:
            self._cached_memory = None
            self._cache_time = 0.0

    @property
    def is_cached(self) -> bool:
        """Check if memory is currently cached."""
        return self._cached_memory is not None


# Global loader instance
_global_loader: MemoryLoader | None = None


def get_memory_loader(
    project_root: Path | None = None,
    directory: Path | None = None,
) -> MemoryLoader:
    """
    Get or create the global memory loader.

    Args:
        project_root: Optional project root path
        directory: Optional directory path

    Returns:
        MemoryLoader instance
    """
    global _global_loader

    if _global_loader is None:
        _global_loader = MemoryLoader(
            project_root=project_root,
            directory=directory,
        )

    return _global_loader


def load_memory(
    project_root: Path | None = None,
    directory: Path | None = None,
    force_refresh: bool = False,
) -> MergedMemory:
    """
    Convenience function to load memory.

    Args:
        project_root: Optional project root path
        directory: Optional directory path
        force_refresh: If True, bypass cache

    Returns:
        MergedMemory
    """
    loader = get_memory_loader(project_root, directory)
    return loader.load(force_refresh)


def get_memory_injection(
    project_root: Path | None = None,
    directory: Path | None = None,
    force_refresh: bool = False,
) -> str:
    """
    Convenience function to get memory for injection.

    Args:
        project_root: Optional project root path
        directory: Optional directory path
        force_refresh: If True, bypass cache

    Returns:
        Formatted string for system prompt injection
    """
    loader = get_memory_loader(project_root, directory)
    return loader.get_injection_content(force_refresh)
