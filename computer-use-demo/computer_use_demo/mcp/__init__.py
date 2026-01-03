"""
Proto MCP (Model Context Protocol) Integration Module.

Provides connectivity to external systems through MCP servers.
MCP servers can provide tools, resources, and prompts.

Configuration (in .claude/settings.json):
    {
        "mcpServers": {
            "filesystem": {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path"],
                "autoStart": true
            },
            "github": {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-github"],
                "env": {"GITHUB_TOKEN": "..."}
            }
        }
    }

Usage:
    from computer_use_demo.mcp import (
        initialize_mcp,
        get_mcp_registry,
        create_all_mcp_tools,
    )

    # Initialize MCP (starts auto-start servers)
    await initialize_mcp()

    # Get tools from all servers
    tools = await create_all_mcp_tools()

    # Call a tool directly
    registry = get_mcp_registry()
    result = await registry.call_tool("read_file", {"path": "/etc/hosts"})
"""

from .client import MCPClient

from .config import (
    get_settings_paths,
    load_mcp_configs,
    load_settings,
    parse_mcp_servers,
    save_mcp_config,
)

from .server_registry import (
    MCPServerRegistry,
    get_mcp_registry,
    initialize_mcp,
    shutdown_mcp,
)

from .tool_wrapper import (
    MCPToolWrapper,
    create_all_mcp_tools,
    create_mcp_tools_from_server,
    get_mcp_tool_by_name,
)

from .types import (
    MCPPrompt,
    MCPRequest,
    MCPResource,
    MCPResponse,
    MCPServerConfig,
    MCPServerInfo,
    MCPServerStatus,
    MCPTool,
)

__all__ = [
    # Types
    "MCPPrompt",
    "MCPRequest",
    "MCPResource",
    "MCPResponse",
    "MCPServerConfig",
    "MCPServerInfo",
    "MCPServerStatus",
    "MCPTool",
    # Client
    "MCPClient",
    # Config
    "get_settings_paths",
    "load_mcp_configs",
    "load_settings",
    "parse_mcp_servers",
    "save_mcp_config",
    # Registry
    "MCPServerRegistry",
    "get_mcp_registry",
    "initialize_mcp",
    "shutdown_mcp",
    # Tool Wrapper
    "MCPToolWrapper",
    "create_all_mcp_tools",
    "create_mcp_tools_from_server",
    "get_mcp_tool_by_name",
]
