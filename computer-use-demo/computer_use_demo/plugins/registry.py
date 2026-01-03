"""
Plugin Registry.

Tracks installed plugins and their status.
"""

import json
import threading
from pathlib import Path
from typing import Any, Callable

from .types import (
    Plugin,
    PluginStatus,
    PluginType,
)


# Type for plugin event callbacks
PluginEventCallback = Callable[[Plugin, str], None]  # plugin, event_type


class PluginRegistry:
    """
    Central registry for all installed plugins.

    Features:
    - Track installed plugins
    - Enable/disable plugins
    - Query plugins by type, status, etc.
    - Event notifications
    """

    def __init__(self, data_dir: Path | None = None):
        self._data_dir = data_dir or Path.home() / ".claude" / "plugins"
        self._data_dir.mkdir(parents=True, exist_ok=True)

        self._plugins: dict[str, Plugin] = {}
        self._lock = threading.Lock()

        # Callbacks
        self._callbacks: list[PluginEventCallback] = []

        # Load registry state
        self._load()

    def _load(self) -> None:
        """Load registry state from disk."""
        registry_file = self._data_dir / "registry.json"
        if registry_file.exists():
            try:
                with open(registry_file, "r") as f:
                    data = json.load(f)

                # Load plugin states (actual plugins loaded by manager)
                self._plugin_states = data.get("plugins", {})
            except Exception:
                self._plugin_states = {}
        else:
            self._plugin_states = {}

    def _save(self) -> None:
        """Save registry state to disk."""
        registry_file = self._data_dir / "registry.json"

        data = {
            "plugins": {
                pid: {
                    "status": p.status.value,
                    "config": p.config,
                }
                for pid, p in self._plugins.items()
            },
        }

        with open(registry_file, "w") as f:
            json.dump(data, f, indent=2)

    def register(self, plugin: Plugin) -> None:
        """
        Register a plugin.

        Args:
            plugin: Plugin to register
        """
        with self._lock:
            # Restore saved state if exists
            if plugin.id in self._plugin_states:
                saved = self._plugin_states[plugin.id]
                plugin.status = PluginStatus(saved.get("status", "installed"))
                plugin.config.update(saved.get("config", {}))

            self._plugins[plugin.id] = plugin
            self._save()

        self._emit_event(plugin, "registered")
        print(f"[Registry] Registered: {plugin.name}")

    def unregister(self, plugin_id: str) -> bool:
        """
        Unregister a plugin.

        Args:
            plugin_id: Plugin identifier

        Returns:
            True if unregistered
        """
        with self._lock:
            plugin = self._plugins.pop(plugin_id, None)
            if plugin:
                self._save()

        if plugin:
            self._emit_event(plugin, "unregistered")
            print(f"[Registry] Unregistered: {plugin.name}")
            return True

        return False

    def get(self, plugin_id: str) -> Plugin | None:
        """Get a plugin by ID."""
        return self._plugins.get(plugin_id)

    def list_all(self) -> list[Plugin]:
        """List all registered plugins."""
        return list(self._plugins.values())

    def list_enabled(self) -> list[Plugin]:
        """List all enabled plugins."""
        return [p for p in self._plugins.values() if p.status == PluginStatus.ENABLED]

    def list_by_type(self, plugin_type: PluginType) -> list[Plugin]:
        """List plugins of a specific type."""
        return [p for p in self._plugins.values() if p.type == plugin_type]

    def list_by_status(self, status: PluginStatus) -> list[Plugin]:
        """List plugins with a specific status."""
        return [p for p in self._plugins.values() if p.status == status]

    def search(
        self,
        query: str | None = None,
        plugin_type: PluginType | None = None,
        enabled_only: bool = False,
    ) -> list[Plugin]:
        """
        Search plugins.

        Args:
            query: Search query (matches id, name, description, keywords)
            plugin_type: Filter by type
            enabled_only: Only return enabled plugins

        Returns:
            Matching plugins
        """
        results = list(self._plugins.values())

        if enabled_only:
            results = [p for p in results if p.status == PluginStatus.ENABLED]

        if plugin_type:
            results = [p for p in results if p.type == plugin_type]

        if query:
            query_lower = query.lower()
            results = [
                p for p in results
                if (
                    query_lower in p.id.lower()
                    or query_lower in p.name.lower()
                    or query_lower in p.manifest.description.lower()
                    or any(query_lower in kw.lower() for kw in p.manifest.keywords)
                )
            ]

        return results

    def enable(self, plugin_id: str) -> bool:
        """
        Enable a plugin.

        Args:
            plugin_id: Plugin identifier

        Returns:
            True if enabled
        """
        with self._lock:
            plugin = self._plugins.get(plugin_id)
            if not plugin:
                return False

            if plugin.status == PluginStatus.ERROR:
                return False

            plugin.status = PluginStatus.ENABLED
            self._save()

        self._emit_event(plugin, "enabled")
        print(f"[Registry] Enabled: {plugin.name}")
        return True

    def disable(self, plugin_id: str) -> bool:
        """
        Disable a plugin.

        Args:
            plugin_id: Plugin identifier

        Returns:
            True if disabled
        """
        with self._lock:
            plugin = self._plugins.get(plugin_id)
            if not plugin:
                return False

            plugin.status = PluginStatus.DISABLED
            self._save()

        self._emit_event(plugin, "disabled")
        print(f"[Registry] Disabled: {plugin.name}")
        return True

    def update_config(self, plugin_id: str, config: dict[str, Any]) -> bool:
        """
        Update plugin configuration.

        Args:
            plugin_id: Plugin identifier
            config: New configuration values

        Returns:
            True if updated
        """
        with self._lock:
            plugin = self._plugins.get(plugin_id)
            if not plugin:
                return False

            plugin.config.update(config)

            # Save to plugin config file
            config_path = plugin.path / "config.json"
            with open(config_path, "w") as f:
                json.dump(plugin.config, f, indent=2)

            self._save()

        self._emit_event(plugin, "config_updated")
        return True

    def get_all_skills(self) -> list[Path]:
        """Get all skill paths from enabled plugins."""
        paths = []
        for plugin in self.list_enabled():
            paths.extend(plugin.get_skill_paths())
        return paths

    def get_all_rules(self) -> list[Path]:
        """Get all rule paths from enabled plugins."""
        paths = []
        for plugin in self.list_enabled():
            paths.extend(plugin.get_rule_paths())
        return paths

    def get_all_hooks(self) -> list[Path]:
        """Get all hook config paths from enabled plugins."""
        paths = []
        for plugin in self.list_enabled():
            paths.extend(plugin.get_hook_paths())
        return paths

    def on_event(self, callback: PluginEventCallback) -> None:
        """Register callback for plugin events."""
        self._callbacks.append(callback)

    def _emit_event(self, plugin: Plugin, event_type: str) -> None:
        """Emit a plugin event."""
        for callback in self._callbacks:
            try:
                callback(plugin, event_type)
            except Exception:
                pass

    def get_stats(self) -> dict[str, Any]:
        """Get registry statistics."""
        plugins = list(self._plugins.values())

        return {
            "total_plugins": len(plugins),
            "enabled_plugins": len([p for p in plugins if p.status == PluginStatus.ENABLED]),
            "disabled_plugins": len([p for p in plugins if p.status == PluginStatus.DISABLED]),
            "error_plugins": len([p for p in plugins if p.status == PluginStatus.ERROR]),
            "by_type": {
                t.value: len([p for p in plugins if p.type == t])
                for t in PluginType
                if any(p.type == t for p in plugins)
            },
        }
