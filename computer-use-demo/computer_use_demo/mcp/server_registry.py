"""
MCP server registry.

Manages the lifecycle of MCP server processes.
"""

import asyncio
import threading
from pathlib import Path
from typing import Any

from .client import MCPClient
from .config import load_mcp_configs
from .types import (
    MCPPrompt,
    MCPResource,
    MCPServerConfig,
    MCPServerInfo,
    MCPServerStatus,
    MCPTool,
)


class MCPServerRegistry:
    """
    Registry for managing MCP servers.

    Handles:
    - Starting/stopping servers
    - Health monitoring
    - Tool/resource/prompt discovery
    """

    def __init__(self, project_root: Path | None = None):
        self._project_root = project_root
        self._clients: dict[str, MCPClient] = {}
        self._configs: dict[str, MCPServerConfig] = {}
        self._lock = threading.Lock()
        self._initialized = False

    async def initialize(self, auto_start: bool = True) -> None:
        """
        Initialize the registry by loading configs and optionally starting servers.

        Args:
            auto_start: Whether to start servers marked for auto-start
        """
        if self._initialized:
            return

        # Load configurations
        configs = load_mcp_configs(self._project_root)

        with self._lock:
            for config in configs:
                self._configs[config.name] = config

        # Start auto-start servers
        if auto_start:
            for config in configs:
                if config.auto_start and config.enabled:
                    try:
                        await self.start_server(config.name)
                    except Exception as e:
                        print(f"[MCP] Failed to auto-start server '{config.name}': {e}")

        self._initialized = True

    async def shutdown(self) -> None:
        """Stop all servers and clean up."""
        with self._lock:
            servers = list(self._clients.keys())

        for name in servers:
            try:
                await self.stop_server(name)
            except Exception:
                pass

        self._initialized = False

    def add_server_config(self, config: MCPServerConfig) -> None:
        """Add a server configuration."""
        with self._lock:
            self._configs[config.name] = config

    def remove_server_config(self, name: str) -> None:
        """Remove a server configuration."""
        with self._lock:
            self._configs.pop(name, None)

    async def start_server(self, name: str) -> MCPClient:
        """
        Start an MCP server.

        Args:
            name: Server name

        Returns:
            MCPClient for the server
        """
        with self._lock:
            # Check if already running
            if name in self._clients:
                client = self._clients[name]
                if client.is_running:
                    return client

            # Get config
            config = self._configs.get(name)
            if not config:
                raise ValueError(f"Unknown MCP server: {name}")

            # Create client
            client = MCPClient(config)

        # Start server (outside lock)
        await client.start()

        with self._lock:
            self._clients[name] = client

        return client

    async def stop_server(self, name: str) -> None:
        """Stop an MCP server."""
        with self._lock:
            client = self._clients.pop(name, None)

        if client:
            await client.stop()

    async def restart_server(self, name: str) -> MCPClient:
        """Restart an MCP server."""
        await self.stop_server(name)
        return await self.start_server(name)

    def get_client(self, name: str) -> MCPClient | None:
        """Get the client for a server."""
        with self._lock:
            return self._clients.get(name)

    def get_running_servers(self) -> list[str]:
        """Get names of running servers."""
        with self._lock:
            return [
                name for name, client in self._clients.items()
                if client.is_running
            ]

    def get_server_info(self, name: str) -> MCPServerInfo | None:
        """Get info about a server."""
        with self._lock:
            client = self._clients.get(name)
            config = self._configs.get(name)

        if not config:
            return None

        info = MCPServerInfo(
            name=name,
            status=client.status if client else MCPServerStatus.STOPPED,
            pid=client._process.pid if client and client._process else None,
        )

        return info

    def list_servers(self) -> list[MCPServerInfo]:
        """List all configured servers."""
        servers = []

        with self._lock:
            for name in self._configs:
                client = self._clients.get(name)
                config = self._configs[name]

                info = MCPServerInfo(
                    name=name,
                    status=client.status if client else MCPServerStatus.STOPPED,
                    pid=client._process.pid if client and client._process else None,
                )
                servers.append(info)

        return servers

    async def list_all_tools(self) -> list[MCPTool]:
        """List tools from all running servers."""
        all_tools = []

        for name in self.get_running_servers():
            client = self.get_client(name)
            if client:
                try:
                    tools = await client.list_tools()
                    all_tools.extend(tools)
                except Exception:
                    pass

        return all_tools

    async def list_all_resources(self) -> list[MCPResource]:
        """List resources from all running servers."""
        all_resources = []

        for name in self.get_running_servers():
            client = self.get_client(name)
            if client:
                try:
                    resources = await client.list_resources()
                    all_resources.extend(resources)
                except Exception:
                    pass

        return all_resources

    async def list_all_prompts(self) -> list[MCPPrompt]:
        """List prompts from all running servers."""
        all_prompts = []

        for name in self.get_running_servers():
            client = self.get_client(name)
            if client:
                try:
                    prompts = await client.list_prompts()
                    all_prompts.extend(prompts)
                except Exception:
                    pass

        return all_prompts

    async def call_tool(
        self,
        tool_name: str,
        arguments: dict[str, Any] | None = None,
        server_name: str | None = None,
    ) -> Any:
        """
        Call a tool.

        If server_name is not provided, searches all servers for the tool.

        Args:
            tool_name: Tool name
            arguments: Tool arguments
            server_name: Optional server to call on

        Returns:
            Tool result
        """
        if server_name:
            client = self.get_client(server_name)
            if not client or not client.is_running:
                raise RuntimeError(f"Server '{server_name}' is not running")
            return await client.call_tool(tool_name, arguments)

        # Search all servers for the tool
        for name in self.get_running_servers():
            client = self.get_client(name)
            if client:
                try:
                    tools = await client.list_tools()
                    if any(t.name == tool_name for t in tools):
                        return await client.call_tool(tool_name, arguments)
                except Exception:
                    pass

        raise ValueError(f"Tool '{tool_name}' not found on any server")


# Global registry instance
_global_registry: MCPServerRegistry | None = None


def get_mcp_registry(project_root: Path | None = None) -> MCPServerRegistry:
    """Get or create the global MCP server registry."""
    global _global_registry

    if _global_registry is None:
        _global_registry = MCPServerRegistry(project_root)

    return _global_registry


async def initialize_mcp(
    project_root: Path | None = None,
    auto_start: bool = True,
) -> MCPServerRegistry:
    """
    Initialize MCP support.

    Args:
        project_root: Optional project root path
        auto_start: Whether to auto-start configured servers

    Returns:
        MCPServerRegistry
    """
    registry = get_mcp_registry(project_root)
    await registry.initialize(auto_start)
    return registry


async def shutdown_mcp() -> None:
    """Shutdown all MCP servers."""
    global _global_registry

    if _global_registry:
        await _global_registry.shutdown()
        _global_registry = None
