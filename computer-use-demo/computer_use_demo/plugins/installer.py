"""
Plugin Installer.

Installs plugins from remote sources (npm, git, local).
"""

import json
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from .types import (
    Plugin,
    PluginManifest,
    PluginStatus,
)
from .loader import PluginLoader


class PluginInstaller:
    """
    Installs plugins from various sources.

    Supported sources:
    - npm: @scope/package-name
    - git: https://github.com/user/repo
    - local: /path/to/plugin
    - marketplace: proto://marketplace/plugin-id
    """

    def __init__(
        self,
        plugins_dir: Path | None = None,
        marketplace_url: str = "https://registry.anthropic.com",
    ):
        self._plugins_dir = plugins_dir or Path.home() / ".claude" / "plugins"
        self._plugins_dir.mkdir(parents=True, exist_ok=True)
        self._marketplace_url = marketplace_url
        self._loader = PluginLoader(self._plugins_dir)

    async def install(
        self,
        source: str,
        force: bool = False,
    ) -> Plugin | None:
        """
        Install a plugin from a source.

        Args:
            source: Plugin source (npm package, git URL, local path, etc.)
            force: Overwrite if already installed

        Returns:
            Installed plugin or None if failed
        """
        # Determine source type
        if source.startswith("@"):
            return await self._install_from_npm(source, force)
        elif source.startswith("https://") or source.startswith("git@"):
            return await self._install_from_git(source, force)
        elif source.startswith("/") or source.startswith("./"):
            return await self._install_from_local(source, force)
        elif source.startswith("proto://"):
            return await self._install_from_marketplace(source, force)
        else:
            # Assume npm package
            return await self._install_from_npm(source, force)

    async def _install_from_npm(
        self,
        package: str,
        force: bool = False,
    ) -> Plugin | None:
        """Install from npm."""
        print(f"[Installer] Installing from npm: {package}")

        # Create temp directory for npm install
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            try:
                # Initialize package.json
                init_result = subprocess.run(
                    ["npm", "init", "-y"],
                    cwd=temp_path,
                    capture_output=True,
                    text=True,
                )

                # Install package
                install_result = subprocess.run(
                    ["npm", "install", package],
                    cwd=temp_path,
                    capture_output=True,
                    text=True,
                )

                if install_result.returncode != 0:
                    print(f"[Installer] npm install failed: {install_result.stderr}")
                    return None

                # Find installed package
                node_modules = temp_path / "node_modules"
                package_name = package.split("@")[-1] if "@" in package else package
                package_path = node_modules / package_name

                if not package_path.exists():
                    # Try scoped package path
                    if package.startswith("@"):
                        scope, name = package.split("/")
                        package_path = node_modules / scope / name

                if not package_path.exists():
                    print(f"[Installer] Package not found after install: {package}")
                    return None

                # Copy to plugins directory
                return await self._install_from_local(str(package_path), force)

            except Exception as e:
                print(f"[Installer] npm install error: {e}")
                return None

    async def _install_from_git(
        self,
        url: str,
        force: bool = False,
    ) -> Plugin | None:
        """Install from git repository."""
        print(f"[Installer] Installing from git: {url}")

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            try:
                # Clone repository
                clone_result = subprocess.run(
                    ["git", "clone", "--depth", "1", url, str(temp_path / "repo")],
                    capture_output=True,
                    text=True,
                )

                if clone_result.returncode != 0:
                    print(f"[Installer] git clone failed: {clone_result.stderr}")
                    return None

                repo_path = temp_path / "repo"

                # Check for plugin.json
                if not (repo_path / "plugin.json").exists():
                    print("[Installer] No plugin.json found in repository")
                    return None

                return await self._install_from_local(str(repo_path), force)

            except Exception as e:
                print(f"[Installer] git clone error: {e}")
                return None

    async def _install_from_local(
        self,
        path: str,
        force: bool = False,
    ) -> Plugin | None:
        """Install from local path."""
        source_path = Path(path)

        if not source_path.exists():
            print(f"[Installer] Path not found: {path}")
            return None

        # Load manifest
        manifest_path = source_path / "plugin.json"
        if not manifest_path.exists():
            print(f"[Installer] No plugin.json found at {path}")
            return None

        try:
            with open(manifest_path, "r") as f:
                manifest_data = json.load(f)

            # Validate manifest
            errors = self._loader.validate_manifest(manifest_data)
            if errors:
                print(f"[Installer] Invalid manifest: {errors}")
                return None

            manifest = PluginManifest.from_dict(manifest_data)

            # Check if already installed
            target_path = self._plugins_dir / manifest.id.replace("@", "").replace("/", "_")
            if target_path.exists():
                if force:
                    shutil.rmtree(target_path)
                else:
                    print(f"[Installer] Plugin already installed: {manifest.id}")
                    return self._loader.load(target_path)

            # Copy to plugins directory
            shutil.copytree(source_path, target_path)

            # Load and return
            plugin = self._loader.load(target_path)
            if plugin:
                plugin.status = PluginStatus.INSTALLED
                print(f"[Installer] Installed: {manifest.name} v{manifest.version}")

            return plugin

        except Exception as e:
            print(f"[Installer] Install error: {e}")
            return None

    async def _install_from_marketplace(
        self,
        uri: str,
        force: bool = False,
    ) -> Plugin | None:
        """Install from Proto marketplace."""
        # Parse URI: proto://marketplace/plugin-id
        parsed = urlparse(uri)
        plugin_id = parsed.path.strip("/")

        print(f"[Installer] Installing from marketplace: {plugin_id}")

        # TODO: Implement marketplace API client
        # For now, return None
        print("[Installer] Marketplace installation not yet implemented")
        return None

    async def uninstall(self, plugin_id: str) -> bool:
        """
        Uninstall a plugin.

        Args:
            plugin_id: Plugin identifier

        Returns:
            True if uninstalled
        """
        dir_name = plugin_id.replace("@", "").replace("/", "_")
        plugin_path = self._plugins_dir / dir_name

        if not plugin_path.exists():
            print(f"[Installer] Plugin not found: {plugin_id}")
            return False

        try:
            shutil.rmtree(plugin_path)
            print(f"[Installer] Uninstalled: {plugin_id}")
            return True
        except Exception as e:
            print(f"[Installer] Uninstall error: {e}")
            return False

    async def update(
        self,
        plugin_id: str,
        source: str | None = None,
    ) -> Plugin | None:
        """
        Update a plugin.

        Args:
            plugin_id: Plugin to update
            source: New source (or use original source)

        Returns:
            Updated plugin or None if failed
        """
        dir_name = plugin_id.replace("@", "").replace("/", "_")
        plugin_path = self._plugins_dir / dir_name

        if not plugin_path.exists():
            print(f"[Installer] Plugin not found: {plugin_id}")
            return None

        # Load current plugin to get source
        plugin = self._loader.load(plugin_path)
        if not plugin:
            return None

        # Use provided source or try to infer from metadata
        if not source:
            source = plugin.manifest.repository or plugin.id

        # Reinstall with force
        return await self.install(source, force=True)

    def list_installed(self) -> list[dict[str, Any]]:
        """
        List installed plugins.

        Returns:
            List of plugin info dicts
        """
        plugins = []

        for path in self._plugins_dir.iterdir():
            if path.is_dir():
                manifest_path = path / "plugin.json"
                if manifest_path.exists():
                    try:
                        with open(manifest_path, "r") as f:
                            manifest = json.load(f)
                        plugins.append({
                            "id": manifest.get("id", path.name),
                            "name": manifest.get("name", path.name),
                            "version": manifest.get("version", "unknown"),
                            "type": manifest.get("type", "plugin"),
                            "path": str(path),
                        })
                    except Exception:
                        pass

        return plugins
