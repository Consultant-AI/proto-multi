"""
Proto Plugins System.

Bundles skills, MCPs, hooks, and commands into installable packages.

Usage:
    from computer_use_demo.plugins import (
        get_plugin_manager,
        Plugin,
        PluginType,
    )

    # Get the plugin manager
    manager = get_plugin_manager()

    # Load all installed plugins
    await manager.load_all()

    # Get a specific plugin
    plugin = manager.get("@anthropic/security-suite")

    # Install a plugin
    await manager.install("@community/devops-toolkit")
"""

from .types import (
    Plugin,
    PluginType,
    PluginManifest,
    PluginComponent,
    PluginDependency,
    PluginStatus,
)

from .loader import (
    PluginLoader,
)

from .registry import (
    PluginRegistry,
)

from .manager import (
    PluginManager,
    get_plugin_manager,
    shutdown_plugins,
)

from .installer import (
    PluginInstaller,
)

__all__ = [
    # Types
    "Plugin",
    "PluginType",
    "PluginManifest",
    "PluginComponent",
    "PluginDependency",
    "PluginStatus",
    # Loader
    "PluginLoader",
    # Registry
    "PluginRegistry",
    # Manager
    "PluginManager",
    "get_plugin_manager",
    "shutdown_plugins",
    # Installer
    "PluginInstaller",
]
