"""
Plugin Loader.

Discovers and loads plugins from disk.
"""

import importlib.util
import json
from pathlib import Path
from typing import Any

from .types import (
    Plugin,
    PluginManifest,
    PluginStatus,
    PluginType,
)


class PluginLoader:
    """
    Loads plugins from disk.

    Plugins are stored in directories with a plugin.json manifest.
    """

    def __init__(self, plugins_dir: Path | None = None):
        self._plugins_dir = plugins_dir or Path.home() / ".claude" / "plugins"
        self._plugins_dir.mkdir(parents=True, exist_ok=True)

    @property
    def plugins_dir(self) -> Path:
        return self._plugins_dir

    def discover(self) -> list[Path]:
        """
        Discover all plugin directories.

        Returns:
            List of paths to plugin directories
        """
        plugins = []

        # Each subdirectory with a plugin.json is a plugin
        for path in self._plugins_dir.iterdir():
            if path.is_dir():
                manifest_path = path / "plugin.json"
                if manifest_path.exists():
                    plugins.append(path)

        return plugins

    def load(self, plugin_path: Path) -> Plugin | None:
        """
        Load a plugin from a directory.

        Args:
            plugin_path: Path to plugin directory

        Returns:
            Loaded Plugin or None if failed
        """
        manifest_path = plugin_path / "plugin.json"

        if not manifest_path.exists():
            print(f"[Plugins] No plugin.json found in {plugin_path}")
            return None

        try:
            # Load manifest
            with open(manifest_path, "r") as f:
                manifest_data = json.load(f)

            manifest = PluginManifest.from_dict(manifest_data)

            # Create plugin
            plugin = Plugin(
                manifest=manifest,
                path=plugin_path,
                status=PluginStatus.INSTALLED,
                config=manifest.default_config.copy(),
            )

            # Load user config if exists
            config_path = plugin_path / "config.json"
            if config_path.exists():
                with open(config_path, "r") as f:
                    user_config = json.load(f)
                plugin.config.update(user_config)

            # Load module if has entry point
            if manifest.entry_point:
                plugin.module = self._load_module(plugin_path, manifest.entry_point)

            print(f"[Plugins] Loaded: {manifest.name} v{manifest.version}")
            return plugin

        except Exception as e:
            print(f"[Plugins] Failed to load {plugin_path}: {e}")
            return Plugin(
                manifest=PluginManifest(
                    id=plugin_path.name,
                    name=plugin_path.name,
                    version="0.0.0",
                ),
                path=plugin_path,
                status=PluginStatus.ERROR,
                error=str(e),
            )

    def load_all(self) -> list[Plugin]:
        """
        Load all discovered plugins.

        Returns:
            List of loaded plugins
        """
        plugins = []

        for path in self.discover():
            plugin = self.load(path)
            if plugin:
                plugins.append(plugin)

        return plugins

    def _load_module(self, plugin_path: Path, entry_point: str) -> Any:
        """
        Load a Python module from the plugin.

        Args:
            plugin_path: Plugin directory
            entry_point: Module path (e.g., "main.py" or "src/plugin.py")

        Returns:
            Loaded module
        """
        module_path = plugin_path / entry_point

        if not module_path.exists():
            raise FileNotFoundError(f"Entry point not found: {module_path}")

        spec = importlib.util.spec_from_file_location(
            f"plugin_{plugin_path.name}",
            module_path,
        )

        if not spec or not spec.loader:
            raise ImportError(f"Could not load module spec for {module_path}")

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        return module

    def create_plugin_structure(
        self,
        plugin_id: str,
        name: str,
        plugin_type: PluginType = PluginType.PLUGIN,
        author: str = "",
    ) -> Path:
        """
        Create a new plugin directory structure.

        Args:
            plugin_id: Plugin identifier (e.g., "@user/my-plugin")
            name: Display name
            plugin_type: Type of plugin
            author: Author name

        Returns:
            Path to created plugin directory
        """
        # Convert @scope/name to scope_name for directory
        dir_name = plugin_id.replace("@", "").replace("/", "_")
        plugin_path = self._plugins_dir / dir_name
        plugin_path.mkdir(parents=True, exist_ok=True)

        # Create manifest
        manifest = PluginManifest(
            id=plugin_id,
            name=name,
            version="0.1.0",
            type=plugin_type,
            author=author,
        )

        manifest_path = plugin_path / "plugin.json"
        with open(manifest_path, "w") as f:
            json.dump(manifest.to_dict(), f, indent=2)

        # Create component directories based on type
        if plugin_type == PluginType.PLUGIN:
            (plugin_path / "skills").mkdir(exist_ok=True)
            (plugin_path / "rules").mkdir(exist_ok=True)
            (plugin_path / "hooks").mkdir(exist_ok=True)
        elif plugin_type == PluginType.SKILL:
            (plugin_path / "skills").mkdir(exist_ok=True)
        elif plugin_type == PluginType.RULE:
            (plugin_path / "rules").mkdir(exist_ok=True)

        # Create README
        readme_path = plugin_path / "README.md"
        with open(readme_path, "w") as f:
            f.write(f"# {name}\n\n{manifest.description or 'A Proto plugin.'}\n")

        print(f"[Plugins] Created plugin structure at {plugin_path}")
        return plugin_path

    def validate_manifest(self, manifest_data: dict[str, Any]) -> list[str]:
        """
        Validate a plugin manifest.

        Args:
            manifest_data: Raw manifest data

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        # Required fields
        if not manifest_data.get("id"):
            errors.append("Missing required field: id")
        if not manifest_data.get("name"):
            errors.append("Missing required field: name")
        if not manifest_data.get("version"):
            errors.append("Missing required field: version")

        # Validate ID format
        plugin_id = manifest_data.get("id", "")
        if plugin_id and not (plugin_id.startswith("@") or "/" not in plugin_id):
            if "@" in plugin_id and "/" not in plugin_id:
                errors.append("Invalid id format: should be @scope/name")

        # Validate version format (basic semver)
        version = manifest_data.get("version", "")
        if version:
            parts = version.split(".")
            if len(parts) < 2 or len(parts) > 3:
                errors.append("Invalid version format: should be semver (x.y.z)")

        # Validate components
        for i, comp in enumerate(manifest_data.get("components", [])):
            if not comp.get("type"):
                errors.append(f"Component {i}: missing type")
            if not comp.get("name"):
                errors.append(f"Component {i}: missing name")
            if not comp.get("path"):
                errors.append(f"Component {i}: missing path")

        return errors
