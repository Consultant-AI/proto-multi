"""
Type definitions for the Marketplace.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class PackageType(str, Enum):
    """Types of marketplace packages."""

    SKILL = "skill"
    RULE = "rule"
    HOOK = "hook"
    MCP = "mcp"
    SUBAGENT = "subagent"
    PLUGIN = "plugin"


class RegistryType(str, Enum):
    """Types of registries."""

    ANTHROPIC = "anthropic"  # Official Anthropic registry
    NPM = "npm"  # npm packages
    GITHUB = "github"  # GitHub releases
    CUSTOM = "custom"  # Custom/private registry


@dataclass
class RegistryConfig:
    """Configuration for a registry."""

    # Registry URL
    url: str

    # Registry type
    type: RegistryType = RegistryType.CUSTOM

    # Display name
    name: str = ""

    # Authentication token (if required)
    auth_token: str | None = None

    # Whether registry is enabled
    enabled: bool = True

    # Priority (lower = higher priority)
    priority: int = 100

    def to_dict(self) -> dict[str, Any]:
        return {
            "url": self.url,
            "type": self.type.value,
            "name": self.name,
            "enabled": self.enabled,
            "priority": self.priority,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RegistryConfig":
        return cls(
            url=data["url"],
            type=RegistryType(data.get("type", "custom")),
            name=data.get("name", ""),
            auth_token=data.get("auth_token"),
            enabled=data.get("enabled", True),
            priority=data.get("priority", 100),
        )


@dataclass
class PackageVersion:
    """A specific version of a package."""

    # Version string (semver)
    version: str

    # Release date
    released_at: datetime = field(default_factory=datetime.utcnow)

    # Download URL
    download_url: str = ""

    # SHA256 checksum
    checksum: str = ""

    # Minimum Proto version required
    min_proto_version: str = "0.1.0"

    # Dependencies
    dependencies: dict[str, str] = field(default_factory=dict)

    # Changelog/release notes
    changelog: str = ""


@dataclass
class PackageInfo:
    """Information about a marketplace package."""

    # Package identifier (e.g., "@anthropic/security-suite")
    id: str

    # Display name
    name: str

    # Description
    description: str = ""

    # Author
    author: str = ""

    # Package type
    type: PackageType = PackageType.PLUGIN

    # Latest version
    latest_version: str = "0.0.0"

    # All available versions
    versions: list[PackageVersion] = field(default_factory=list)

    # Keywords for search
    keywords: list[str] = field(default_factory=list)

    # Homepage URL
    homepage: str = ""

    # Repository URL
    repository: str = ""

    # License
    license: str = "MIT"

    # Download count
    downloads: int = 0

    # Star count / rating
    stars: int = 0

    # Created timestamp
    created_at: datetime = field(default_factory=datetime.utcnow)

    # Last updated timestamp
    updated_at: datetime = field(default_factory=datetime.utcnow)

    # Registry it came from
    registry: str = ""

    # Whether it's verified/official
    verified: bool = False

    # Whether it's deprecated
    deprecated: bool = False

    # Deprecation message
    deprecation_message: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "author": self.author,
            "type": self.type.value,
            "latest_version": self.latest_version,
            "keywords": self.keywords,
            "homepage": self.homepage,
            "repository": self.repository,
            "license": self.license,
            "downloads": self.downloads,
            "stars": self.stars,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "registry": self.registry,
            "verified": self.verified,
            "deprecated": self.deprecated,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PackageInfo":
        info = cls(
            id=data["id"],
            name=data["name"],
            description=data.get("description", ""),
            author=data.get("author", ""),
            type=PackageType(data.get("type", "plugin")),
            latest_version=data.get("latest_version", "0.0.0"),
            keywords=data.get("keywords", []),
            homepage=data.get("homepage", ""),
            repository=data.get("repository", ""),
            license=data.get("license", "MIT"),
            downloads=data.get("downloads", 0),
            stars=data.get("stars", 0),
            registry=data.get("registry", ""),
            verified=data.get("verified", False),
            deprecated=data.get("deprecated", False),
            deprecation_message=data.get("deprecation_message", ""),
        )

        if data.get("created_at"):
            info.created_at = datetime.fromisoformat(data["created_at"])
        if data.get("updated_at"):
            info.updated_at = datetime.fromisoformat(data["updated_at"])

        # Parse versions
        for ver_data in data.get("versions", []):
            info.versions.append(PackageVersion(
                version=ver_data["version"],
                download_url=ver_data.get("download_url", ""),
                checksum=ver_data.get("checksum", ""),
                changelog=ver_data.get("changelog", ""),
            ))

        return info


@dataclass
class SearchResult:
    """Result of a marketplace search."""

    # Search query
    query: str

    # Total matches
    total: int = 0

    # Returned packages
    packages: list[PackageInfo] = field(default_factory=list)

    # Page number
    page: int = 1

    # Page size
    page_size: int = 20

    # Search duration in ms
    duration_ms: float = 0.0


@dataclass
class InstallResult:
    """Result of a package installation."""

    # Package ID
    package_id: str

    # Whether installation succeeded
    success: bool

    # Installed version
    version: str = ""

    # Installation path
    path: str = ""

    # Error message if failed
    error: str | None = None

    # Dependencies installed
    dependencies_installed: list[str] = field(default_factory=list)
