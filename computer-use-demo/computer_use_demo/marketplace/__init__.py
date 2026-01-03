"""
Proto Marketplace Module.

Client for searching, browsing, and installing plugins from registries.

Usage:
    from computer_use_demo.marketplace import (
        get_marketplace,
        MarketplaceClient,
        SearchResult,
    )

    # Get the marketplace client
    marketplace = get_marketplace()

    # Search for plugins
    results = await marketplace.search("security")

    # Get plugin details
    details = await marketplace.get_details("@anthropic/security-suite")

    # Install a plugin
    await marketplace.install("@anthropic/security-suite")
"""

from .types import (
    PackageInfo,
    PackageVersion,
    SearchResult,
    RegistryConfig,
    InstallResult,
)

from .client import (
    MarketplaceClient,
    get_marketplace,
)

from .search import (
    SearchEngine,
    SearchFilter,
)

__all__ = [
    # Types
    "PackageInfo",
    "PackageVersion",
    "SearchResult",
    "RegistryConfig",
    "InstallResult",
    # Client
    "MarketplaceClient",
    "get_marketplace",
    # Search
    "SearchEngine",
    "SearchFilter",
]
