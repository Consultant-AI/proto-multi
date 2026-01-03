"""
Plugin Manager.

Central manager for the plugin system.
"""

import asyncio
from pathlib import Path
from typing import Any

from .types import (
    Plugin,
    PluginStatus,
    PluginType,
)
from .loader import PluginLoader
from .registry import PluginRegistry
from .installer import PluginInstaller


class PluginManager:
    """
    Central manager for all plugin operations.

    Combines loader, registry, and installer into a unified interface.
    """

    def __init__(self, plugins_dir: Path | None = None):
        self._plugins_dir = plugins_dir or Path.home() / ".claude" / "plugins"
        self._plugins_dir.mkdir(parents=True, exist_ok=True)

        self._loader = PluginLoader(self._plugins_dir)
        self._registry = PluginRegistry(self._plugins_dir)
        self._installer = PluginInstaller(self._plugins_dir)

        self._initialized = False

    @property
    def plugins_dir(self) -> Path:
        return self._plugins_dir

    @property
    def registry(self) -> PluginRegistry:
        return self._registry

    @property
    def installer(self) -> PluginInstaller:
        return self._installer

    async def initialize(self) -> None:
        """Initialize the plugin manager and load all plugins."""
        if self._initialized:
            return

        await self.load_all()
        self._initialized = True
        print("[PluginManager] Initialized")

    async def load_all(self) -> list[Plugin]:
        """
        Load all plugins from disk.

        Returns:
            List of loaded plugins
        """
        plugins = self._loader.load_all()

        for plugin in plugins:
            self._registry.register(plugin)

        # Auto-enable plugins that were previously enabled
        for plugin in plugins:
            if plugin.status == PluginStatus.ENABLED:
                await self._activate_plugin(plugin)

        return plugins

    async def install(
        self,
        source: str,
        enable: bool = True,
        force: bool = False,
    ) -> Plugin | None:
        """
        Install a plugin from a source.

        Args:
            source: Plugin source
            enable: Auto-enable after install
            force: Overwrite if exists

        Returns:
            Installed plugin
        """
        plugin = await self._installer.install(source, force)

        if plugin:
            self._registry.register(plugin)

            if enable:
                await self.enable(plugin.id)

        return plugin

    async def uninstall(self, plugin_id: str) -> bool:
        """
        Uninstall a plugin.

        Args:
            plugin_id: Plugin identifier

        Returns:
            True if uninstalled
        """
        # Disable first
        await self.disable(plugin_id)

        # Unregister
        self._registry.unregister(plugin_id)

        # Remove files
        return await self._installer.uninstall(plugin_id)

    async def update(
        self,
        plugin_id: str,
        source: str | None = None,
    ) -> Plugin | None:
        """
        Update a plugin.

        Args:
            plugin_id: Plugin to update
            source: New source (optional)

        Returns:
            Updated plugin
        """
        # Remember if was enabled
        plugin = self._registry.get(plugin_id)
        was_enabled = plugin.status == PluginStatus.ENABLED if plugin else False

        # Update
        plugin = await self._installer.update(plugin_id, source)

        if plugin:
            self._registry.register(plugin)

            if was_enabled:
                await self.enable(plugin.id)

        return plugin

    async def enable(self, plugin_id: str) -> bool:
        """
        Enable a plugin.

        Args:
            plugin_id: Plugin identifier

        Returns:
            True if enabled
        """
        plugin = self._registry.get(plugin_id)
        if not plugin:
            return False

        # Activate plugin components
        await self._activate_plugin(plugin)

        return self._registry.enable(plugin_id)

    async def disable(self, plugin_id: str) -> bool:
        """
        Disable a plugin.

        Args:
            plugin_id: Plugin identifier

        Returns:
            True if disabled
        """
        plugin = self._registry.get(plugin_id)
        if not plugin:
            return False

        # Deactivate plugin components
        await self._deactivate_plugin(plugin)

        return self._registry.disable(plugin_id)

    async def _activate_plugin(self, plugin: Plugin) -> None:
        """Activate a plugin's components."""
        # Load skills
        for path in plugin.get_skill_paths():
            if path.exists():
                # Skills module will pick these up
                print(f"[PluginManager] Activating skill: {path}")

        # Load rules
        for path in plugin.get_rule_paths():
            if path.exists():
                # Rules module will pick these up
                print(f"[PluginManager] Activating rule: {path}")

        # Load hooks
        for path in plugin.get_hook_paths():
            if path.exists():
                # Hooks module will pick these up
                print(f"[PluginManager] Activating hooks: {path}")

        # Call plugin's activate method if exists
        if plugin.module and hasattr(plugin.module, "activate"):
            try:
                if asyncio.iscoroutinefunction(plugin.module.activate):
                    await plugin.module.activate(plugin.config)
                else:
                    plugin.module.activate(plugin.config)
            except Exception as e:
                print(f"[PluginManager] Plugin activate error: {e}")

    async def _deactivate_plugin(self, plugin: Plugin) -> None:
        """Deactivate a plugin's components."""
        # Call plugin's deactivate method if exists
        if plugin.module and hasattr(plugin.module, "deactivate"):
            try:
                if asyncio.iscoroutinefunction(plugin.module.deactivate):
                    await plugin.module.deactivate()
                else:
                    plugin.module.deactivate()
            except Exception as e:
                print(f"[PluginManager] Plugin deactivate error: {e}")

    def get(self, plugin_id: str) -> Plugin | None:
        """Get a plugin by ID."""
        return self._registry.get(plugin_id)

    def list_all(self) -> list[Plugin]:
        """List all plugins."""
        return self._registry.list_all()

    def list_enabled(self) -> list[Plugin]:
        """List enabled plugins."""
        return self._registry.list_enabled()

    def search(
        self,
        query: str | None = None,
        plugin_type: PluginType | None = None,
    ) -> list[Plugin]:
        """Search plugins."""
        return self._registry.search(query, plugin_type)

    def configure(self, plugin_id: str, config: dict[str, Any]) -> bool:
        """Update plugin configuration."""
        return self._registry.update_config(plugin_id, config)

    def create(
        self,
        plugin_id: str,
        name: str,
        plugin_type: PluginType = PluginType.PLUGIN,
        author: str = "",
    ) -> Path:
        """
        Create a new plugin.

        Args:
            plugin_id: Plugin identifier
            name: Display name
            plugin_type: Type of plugin
            author: Author name

        Returns:
            Path to created plugin
        """
        return self._loader.create_plugin_structure(
            plugin_id,
            name,
            plugin_type,
            author,
        )

    def get_all_skill_paths(self) -> list[Path]:
        """Get all skill paths from enabled plugins."""
        return self._registry.get_all_skills()

    def get_all_rule_paths(self) -> list[Path]:
        """Get all rule paths from enabled plugins."""
        return self._registry.get_all_rules()

    def get_all_hook_paths(self) -> list[Path]:
        """Get all hook paths from enabled plugins."""
        return self._registry.get_all_hooks()

    def get_stats(self) -> dict[str, Any]:
        """Get plugin manager statistics."""
        return {
            "plugins_dir": str(self._plugins_dir),
            "initialized": self._initialized,
            **self._registry.get_stats(),
        }


# Global plugin manager instance
_global_manager: PluginManager | None = None


def get_plugin_manager() -> PluginManager:
    """Get or create the global plugin manager."""
    global _global_manager

    if _global_manager is None:
        _global_manager = PluginManager()

    return _global_manager


async def shutdown_plugins() -> None:
    """Shutdown the plugin system."""
    global _global_manager

    if _global_manager:
        # Disable all plugins
        for plugin in _global_manager.list_enabled():
            await _global_manager.disable(plugin.id)

        _global_manager = None
