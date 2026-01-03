"""
Type definitions for the Plugins System.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any
from pathlib import Path


class PluginType(str, Enum):
    """Types of plugins."""

    # Single components
    SKILL = "skill"
    RULE = "rule"
    HOOK = "hook"
    MCP = "mcp"
    SUBAGENT = "subagent"
    COMMAND = "command"

    # Bundles
    PLUGIN = "plugin"  # Full bundle of multiple components


class PluginStatus(str, Enum):
    """Status of a plugin."""

    NOT_INSTALLED = "not_installed"
    INSTALLED = "installed"
    ENABLED = "enabled"
    DISABLED = "disabled"
    ERROR = "error"
    UPDATING = "updating"


@dataclass
class PluginDependency:
    """A dependency on another plugin or component."""

    # Plugin identifier (e.g., "@anthropic/security-auditor")
    plugin_id: str

    # Version constraint (e.g., ">=1.0.0", "^2.0.0")
    version: str = "*"

    # Whether this is optional
    optional: bool = False


@dataclass
class PluginComponent:
    """A component within a plugin."""

    # Component type
    type: PluginType

    # Component name
    name: str

    # Path to component file (relative to plugin root)
    path: str

    # Whether component is enabled
    enabled: bool = True

    # Component-specific configuration
    config: dict[str, Any] = field(default_factory=dict)


@dataclass
class PluginManifest:
    """Plugin manifest (plugin.json)."""

    # Plugin identifier (e.g., "@anthropic/security-suite")
    id: str

    # Display name
    name: str

    # Version (semver)
    version: str

    # Description
    description: str = ""

    # Author
    author: str = ""

    # Author email
    email: str = ""

    # Homepage URL
    homepage: str = ""

    # Repository URL
    repository: str = ""

    # License
    license: str = "MIT"

    # Plugin type
    type: PluginType = PluginType.PLUGIN

    # Keywords for search
    keywords: list[str] = field(default_factory=list)

    # Components included
    components: list[PluginComponent] = field(default_factory=list)

    # Dependencies
    dependencies: list[PluginDependency] = field(default_factory=list)

    # Minimum Proto version required
    min_proto_version: str = "0.1.0"

    # Entry point (for plugins with code)
    entry_point: str | None = None

    # Configuration schema
    config_schema: dict[str, Any] = field(default_factory=dict)

    # Default configuration
    default_config: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "author": self.author,
            "email": self.email,
            "homepage": self.homepage,
            "repository": self.repository,
            "license": self.license,
            "type": self.type.value,
            "keywords": self.keywords,
            "components": [
                {
                    "type": c.type.value,
                    "name": c.name,
                    "path": c.path,
                    "enabled": c.enabled,
                    "config": c.config,
                }
                for c in self.components
            ],
            "dependencies": [
                {
                    "plugin_id": d.plugin_id,
                    "version": d.version,
                    "optional": d.optional,
                }
                for d in self.dependencies
            ],
            "min_proto_version": self.min_proto_version,
            "entry_point": self.entry_point,
            "config_schema": self.config_schema,
            "default_config": self.default_config,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PluginManifest":
        """Create from dictionary."""
        manifest = cls(
            id=data["id"],
            name=data["name"],
            version=data["version"],
            description=data.get("description", ""),
            author=data.get("author", ""),
            email=data.get("email", ""),
            homepage=data.get("homepage", ""),
            repository=data.get("repository", ""),
            license=data.get("license", "MIT"),
            type=PluginType(data.get("type", "plugin")),
            keywords=data.get("keywords", []),
            min_proto_version=data.get("min_proto_version", "0.1.0"),
            entry_point=data.get("entry_point"),
            config_schema=data.get("config_schema", {}),
            default_config=data.get("default_config", {}),
        )

        # Parse components
        for comp_data in data.get("components", []):
            manifest.components.append(PluginComponent(
                type=PluginType(comp_data["type"]),
                name=comp_data["name"],
                path=comp_data["path"],
                enabled=comp_data.get("enabled", True),
                config=comp_data.get("config", {}),
            ))

        # Parse dependencies
        for dep_data in data.get("dependencies", []):
            manifest.dependencies.append(PluginDependency(
                plugin_id=dep_data["plugin_id"],
                version=dep_data.get("version", "*"),
                optional=dep_data.get("optional", False),
            ))

        return manifest


@dataclass
class Plugin:
    """A loaded plugin."""

    # Plugin manifest
    manifest: PluginManifest

    # Installation path
    path: Path

    # Current status
    status: PluginStatus = PluginStatus.INSTALLED

    # User configuration (merged with defaults)
    config: dict[str, Any] = field(default_factory=dict)

    # Installation timestamp
    installed_at: datetime = field(default_factory=datetime.utcnow)

    # Last update timestamp
    updated_at: datetime = field(default_factory=datetime.utcnow)

    # Error message if status is ERROR
    error: str | None = None

    # Loaded module (if has entry_point)
    module: Any = None

    @property
    def id(self) -> str:
        return self.manifest.id

    @property
    def name(self) -> str:
        return self.manifest.name

    @property
    def version(self) -> str:
        return self.manifest.version

    @property
    def type(self) -> PluginType:
        return self.manifest.type

    def get_component(self, name: str) -> PluginComponent | None:
        """Get a component by name."""
        for comp in self.manifest.components:
            if comp.name == name:
                return comp
        return None

    def get_components_by_type(self, comp_type: PluginType) -> list[PluginComponent]:
        """Get all components of a type."""
        return [c for c in self.manifest.components if c.type == comp_type]

    def get_skill_paths(self) -> list[Path]:
        """Get paths to all skill files."""
        return [
            self.path / c.path
            for c in self.manifest.components
            if c.type == PluginType.SKILL and c.enabled
        ]

    def get_rule_paths(self) -> list[Path]:
        """Get paths to all rule files."""
        return [
            self.path / c.path
            for c in self.manifest.components
            if c.type == PluginType.RULE and c.enabled
        ]

    def get_hook_paths(self) -> list[Path]:
        """Get paths to all hook config files."""
        return [
            self.path / c.path
            for c in self.manifest.components
            if c.type == PluginType.HOOK and c.enabled
        ]

    def is_enabled(self) -> bool:
        """Check if plugin is enabled."""
        return self.status == PluginStatus.ENABLED

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "manifest": self.manifest.to_dict(),
            "path": str(self.path),
            "status": self.status.value,
            "config": self.config,
            "installed_at": self.installed_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "error": self.error,
        }
