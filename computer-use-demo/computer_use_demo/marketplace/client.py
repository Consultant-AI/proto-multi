"""
Marketplace Client.

Client for interacting with plugin registries.
"""

import json
from pathlib import Path
from typing import Any

from .types import (
    InstallResult,
    PackageInfo,
    PackageType,
    RegistryConfig,
    RegistryType,
    SearchResult,
)
from .search import SearchEngine, SearchFilter


# Default registries
DEFAULT_REGISTRIES = [
    RegistryConfig(
        url="https://registry.anthropic.com",
        type=RegistryType.ANTHROPIC,
        name="Anthropic Official",
        priority=10,
    ),
    RegistryConfig(
        url="https://registry.npmjs.org",
        type=RegistryType.NPM,
        name="npm",
        priority=50,
    ),
]


class MarketplaceClient:
    """
    Client for marketplace operations.

    Features:
    - Search across registries
    - Get package details
    - Install/uninstall packages
    - Manage registries
    """

    def __init__(self, config_path: Path | None = None):
        self._config_path = config_path or Path.home() / ".proto" / "marketplace.json"
        self._config_path.parent.mkdir(parents=True, exist_ok=True)

        self._registries: list[RegistryConfig] = []
        self._search_engine = SearchEngine()
        self._plugin_manager = None  # Will be set lazily

        # Local package cache
        self._package_cache: dict[str, PackageInfo] = {}

        # Load config
        self._load_config()

    def _load_config(self) -> None:
        """Load marketplace configuration."""
        if self._config_path.exists():
            try:
                with open(self._config_path, "r") as f:
                    data = json.load(f)

                self._registries = [
                    RegistryConfig.from_dict(r)
                    for r in data.get("registries", [])
                ]
            except Exception:
                self._registries = DEFAULT_REGISTRIES.copy()
        else:
            self._registries = DEFAULT_REGISTRIES.copy()
            self._save_config()

    def _save_config(self) -> None:
        """Save marketplace configuration."""
        data = {
            "registries": [r.to_dict() for r in self._registries],
        }

        with open(self._config_path, "w") as f:
            json.dump(data, f, indent=2)

    def _get_plugin_manager(self):
        """Get the plugin manager lazily."""
        if self._plugin_manager is None:
            from ..plugins import get_plugin_manager
            self._plugin_manager = get_plugin_manager()
        return self._plugin_manager

    async def search(
        self,
        query: str,
        filters: SearchFilter | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> SearchResult:
        """
        Search for packages across all registries.

        Args:
            query: Search query
            filters: Optional filters
            page: Page number
            page_size: Results per page

        Returns:
            Search result
        """
        all_packages = []

        # Fetch from each enabled registry
        for registry in self._registries:
            if not registry.enabled:
                continue

            try:
                packages = await self._search_registry(registry, query, filters)
                for pkg in packages:
                    pkg.registry = registry.name
                all_packages.extend(packages)
            except Exception as e:
                print(f"[Marketplace] Error searching {registry.name}: {e}")

        # Use local search engine for ranking and pagination
        return self._search_engine.search_local(
            all_packages,
            query,
            filters,
            page,
            page_size,
        )

    async def _search_registry(
        self,
        registry: RegistryConfig,
        query: str,
        filters: SearchFilter | None,
    ) -> list[PackageInfo]:
        """Search a specific registry."""
        # For now, return empty list - actual implementation would use HTTP
        # This is a placeholder for the registry API calls

        if registry.type == RegistryType.ANTHROPIC:
            return await self._search_anthropic_registry(registry, query, filters)
        elif registry.type == RegistryType.NPM:
            return await self._search_npm_registry(registry, query, filters)
        else:
            return await self._search_custom_registry(registry, query, filters)

    async def _search_anthropic_registry(
        self,
        registry: RegistryConfig,
        query: str,
        filters: SearchFilter | None,
    ) -> list[PackageInfo]:
        """Search Anthropic official registry."""
        # Placeholder - would make HTTP request to registry
        # For demo, return sample packages

        if not query:
            return []

        # Sample packages for demonstration
        sample_packages = [
            PackageInfo(
                id="@anthropic/security-auditor",
                name="Security Auditor",
                description="Expert security code reviewer and vulnerability scanner",
                author="Anthropic",
                type=PackageType.SUBAGENT,
                latest_version="1.0.0",
                keywords=["security", "audit", "vulnerability", "code-review"],
                verified=True,
                downloads=50000,
                stars=500,
            ),
            PackageInfo(
                id="@anthropic/code-review",
                name="Code Review Skill",
                description="Best practices code review guidelines and patterns",
                author="Anthropic",
                type=PackageType.SKILL,
                latest_version="1.2.0",
                keywords=["code-review", "best-practices", "patterns"],
                verified=True,
                downloads=100000,
                stars=1000,
            ),
            PackageInfo(
                id="@anthropic/security-suite",
                name="Security Suite",
                description="Complete security toolkit with skills, rules, and MCP integrations",
                author="Anthropic",
                type=PackageType.PLUGIN,
                latest_version="2.0.0",
                keywords=["security", "owasp", "audit", "compliance"],
                verified=True,
                downloads=75000,
                stars=750,
            ),
        ]

        # Filter by query
        query_lower = query.lower()
        return [
            p for p in sample_packages
            if (
                query_lower in p.name.lower()
                or query_lower in p.description.lower()
                or any(query_lower in kw for kw in p.keywords)
            )
        ]

    async def _search_npm_registry(
        self,
        registry: RegistryConfig,
        query: str,
        filters: SearchFilter | None,
    ) -> list[PackageInfo]:
        """Search npm registry."""
        # Placeholder - would make HTTP request to npm
        return []

    async def _search_custom_registry(
        self,
        registry: RegistryConfig,
        query: str,
        filters: SearchFilter | None,
    ) -> list[PackageInfo]:
        """Search custom registry."""
        # Placeholder - would make HTTP request to custom registry
        return []

    async def get_details(self, package_id: str) -> PackageInfo | None:
        """
        Get detailed information about a package.

        Args:
            package_id: Package identifier

        Returns:
            Package info or None if not found
        """
        # Check cache
        if package_id in self._package_cache:
            return self._package_cache[package_id]

        # Search each registry
        for registry in self._registries:
            if not registry.enabled:
                continue

            try:
                info = await self._get_package_from_registry(registry, package_id)
                if info:
                    self._package_cache[package_id] = info
                    return info
            except Exception:
                pass

        return None

    async def _get_package_from_registry(
        self,
        registry: RegistryConfig,
        package_id: str,
    ) -> PackageInfo | None:
        """Get package details from a registry."""
        # Placeholder - would make HTTP request
        # For demo, return from search if matching

        results = await self._search_registry(registry, package_id, None)
        for pkg in results:
            if pkg.id == package_id:
                return pkg
        return None

    async def install(
        self,
        package_id: str,
        version: str | None = None,
    ) -> InstallResult:
        """
        Install a package.

        Args:
            package_id: Package to install
            version: Specific version (or latest)

        Returns:
            Installation result
        """
        # Get package info
        info = await self.get_details(package_id)
        if not info:
            return InstallResult(
                package_id=package_id,
                success=False,
                error=f"Package not found: {package_id}",
            )

        version = version or info.latest_version

        try:
            # Use plugin manager to install
            manager = self._get_plugin_manager()

            # Determine source based on package info
            if info.repository:
                source = info.repository
            elif "@" in package_id:
                source = package_id  # npm package
            else:
                return InstallResult(
                    package_id=package_id,
                    success=False,
                    error="No installation source available",
                )

            plugin = await manager.install(source, enable=True)

            if plugin:
                return InstallResult(
                    package_id=package_id,
                    success=True,
                    version=version,
                    path=str(plugin.path),
                )
            else:
                return InstallResult(
                    package_id=package_id,
                    success=False,
                    error="Installation failed",
                )

        except Exception as e:
            return InstallResult(
                package_id=package_id,
                success=False,
                error=str(e),
            )

    async def uninstall(self, package_id: str) -> bool:
        """
        Uninstall a package.

        Args:
            package_id: Package to uninstall

        Returns:
            True if uninstalled
        """
        manager = self._get_plugin_manager()
        return await manager.uninstall(package_id)

    async def update(
        self,
        package_id: str,
        version: str | None = None,
    ) -> InstallResult:
        """
        Update a package.

        Args:
            package_id: Package to update
            version: Target version (or latest)

        Returns:
            Update result
        """
        # Get latest info
        info = await self.get_details(package_id)
        if not info:
            return InstallResult(
                package_id=package_id,
                success=False,
                error=f"Package not found: {package_id}",
            )

        version = version or info.latest_version

        try:
            manager = self._get_plugin_manager()
            plugin = await manager.update(package_id)

            if plugin:
                return InstallResult(
                    package_id=package_id,
                    success=True,
                    version=version,
                    path=str(plugin.path),
                )
            else:
                return InstallResult(
                    package_id=package_id,
                    success=False,
                    error="Update failed",
                )

        except Exception as e:
            return InstallResult(
                package_id=package_id,
                success=False,
                error=str(e),
            )

    def add_registry(self, registry: RegistryConfig) -> None:
        """Add a registry."""
        self._registries.append(registry)
        self._registries.sort(key=lambda r: r.priority)
        self._save_config()

    def remove_registry(self, url: str) -> bool:
        """Remove a registry by URL."""
        for i, reg in enumerate(self._registries):
            if reg.url == url:
                self._registries.pop(i)
                self._save_config()
                return True
        return False

    def list_registries(self) -> list[RegistryConfig]:
        """List all configured registries."""
        return self._registries.copy()

    def enable_registry(self, url: str) -> bool:
        """Enable a registry."""
        for reg in self._registries:
            if reg.url == url:
                reg.enabled = True
                self._save_config()
                return True
        return False

    def disable_registry(self, url: str) -> bool:
        """Disable a registry."""
        for reg in self._registries:
            if reg.url == url:
                reg.enabled = False
                self._save_config()
                return True
        return False

    def get_stats(self) -> dict[str, Any]:
        """Get marketplace statistics."""
        return {
            "registries": len(self._registries),
            "enabled_registries": len([r for r in self._registries if r.enabled]),
            "cached_packages": len(self._package_cache),
        }


# Global marketplace client
_global_marketplace: MarketplaceClient | None = None


def get_marketplace() -> MarketplaceClient:
    """Get or create the global marketplace client."""
    global _global_marketplace

    if _global_marketplace is None:
        _global_marketplace = MarketplaceClient()

    return _global_marketplace
