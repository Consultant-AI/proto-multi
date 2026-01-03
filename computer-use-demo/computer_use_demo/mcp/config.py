"""
MCP configuration loader.

Loads MCP server configurations from .claude/settings.json
"""

import json
from pathlib import Path
from typing import Any

from .types import MCPServerConfig


def get_settings_paths() -> list[Path]:
    """Get paths to settings files (enterprise and project)."""
    paths = []

    # Enterprise settings
    enterprise = Path.home() / ".claude" / "settings.json"
    if enterprise.exists():
        paths.append(enterprise)

    # Project settings (search upward)
    current = Path.cwd()
    indicators = [".git", ".claude", "package.json", "pyproject.toml"]

    while current != current.parent:
        for indicator in indicators:
            if (current / indicator).exists():
                project_settings = current / ".claude" / "settings.json"
                if project_settings.exists() and project_settings not in paths:
                    paths.append(project_settings)
                break
        current = current.parent

    return paths


def load_settings(path: Path) -> dict[str, Any]:
    """Load settings from a JSON file."""
    try:
        with open(path, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {}


def parse_mcp_servers(settings: dict[str, Any]) -> list[MCPServerConfig]:
    """
    Parse MCP server configurations from settings.

    Settings format:
    {
        "mcpServers": {
            "filesystem": {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/dir"],
                "env": {},
                "autoStart": true
            },
            "github": {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-github"],
                "env": {"GITHUB_TOKEN": "..."}
            }
        }
    }
    """
    configs = []

    mcp_servers = settings.get("mcpServers", {})

    for name, server_config in mcp_servers.items():
        if not isinstance(server_config, dict):
            continue

        command = server_config.get("command", "")
        if not command:
            continue

        config = MCPServerConfig(
            name=name,
            command=command,
            args=server_config.get("args", []),
            env=server_config.get("env", {}),
            cwd=server_config.get("cwd"),
            auto_start=server_config.get("autoStart", True),
            startup_timeout=server_config.get("startupTimeout", 30.0),
            enabled=server_config.get("enabled", True),
        )
        configs.append(config)

    return configs


def load_mcp_configs(
    project_root: Path | None = None,
    include_enterprise: bool = True,
) -> list[MCPServerConfig]:
    """
    Load all MCP server configurations.

    Args:
        project_root: Optional project root path
        include_enterprise: Whether to include enterprise settings

    Returns:
        List of MCPServerConfig (later settings override earlier)
    """
    all_configs: dict[str, MCPServerConfig] = {}

    paths = get_settings_paths()

    # If project root specified, add its settings
    if project_root:
        project_settings = project_root / ".claude" / "settings.json"
        if project_settings.exists() and project_settings not in paths:
            paths.append(project_settings)

    for path in paths:
        # Skip enterprise if not wanted
        if not include_enterprise and str(Path.home()) in str(path):
            continue

        settings = load_settings(path)
        configs = parse_mcp_servers(settings)

        # Later configs override earlier (by name)
        for config in configs:
            all_configs[config.name] = config

    return list(all_configs.values())


def save_mcp_config(
    name: str,
    config: MCPServerConfig,
    path: Path | None = None,
) -> None:
    """
    Save an MCP server configuration to settings.

    Args:
        name: Server name
        config: Server configuration
        path: Path to settings file (defaults to project settings)
    """
    if path is None:
        # Default to project settings
        paths = get_settings_paths()
        path = paths[-1] if paths else Path.cwd() / ".claude" / "settings.json"

    # Ensure directory exists
    path.parent.mkdir(parents=True, exist_ok=True)

    # Load existing settings
    settings = load_settings(path) if path.exists() else {}

    # Update mcpServers
    if "mcpServers" not in settings:
        settings["mcpServers"] = {}

    settings["mcpServers"][name] = {
        "command": config.command,
        "args": config.args,
        "env": config.env,
        "cwd": config.cwd,
        "autoStart": config.auto_start,
        "startupTimeout": config.startup_timeout,
        "enabled": config.enabled,
    }

    # Save
    with open(path, "w") as f:
        json.dump(settings, f, indent=2)
