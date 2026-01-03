"""
MCP tool wrapper.

Wraps MCP tools as BaseAnthropicTool subclasses so they can be used
by agents alongside native tools.
"""

from typing import Any

from anthropic.types.beta import BetaToolUnionParam

from ..tools.base import BaseAnthropicTool, ToolError, ToolResult
from .server_registry import get_mcp_registry
from .types import MCPTool


class MCPToolWrapper(BaseAnthropicTool):
    """
    Wraps an MCP tool as a BaseAnthropicTool.

    This allows MCP tools to be used seamlessly alongside native tools.
    """

    def __init__(self, mcp_tool: MCPTool):
        self._mcp_tool = mcp_tool
        self._server_name = mcp_tool.server_name

    @property
    def name(self) -> str:
        # Prefix with mcp_ to avoid conflicts and make it clear this is an MCP tool
        return f"mcp_{self._server_name}_{self._mcp_tool.name}"

    def to_params(self) -> BetaToolUnionParam:
        """Convert to Anthropic tool parameters."""
        # Build input schema
        input_schema = self._mcp_tool.input_schema.copy()

        # Ensure it has required fields
        if "type" not in input_schema:
            input_schema["type"] = "object"
        if "properties" not in input_schema:
            input_schema["properties"] = {}

        return {
            "name": self.name,
            "description": self._mcp_tool.description or f"MCP tool from {self._server_name}",
            "input_schema": input_schema,
        }

    async def __call__(self, **kwargs) -> ToolResult:
        """Execute the MCP tool."""
        try:
            registry = get_mcp_registry()
            result = await registry.call_tool(
                tool_name=self._mcp_tool.name,
                arguments=kwargs,
                server_name=self._server_name,
            )

            # Format result
            if isinstance(result, dict):
                # MCP tools typically return content array
                content = result.get("content", [])
                if content:
                    # Extract text from content
                    text_parts = []
                    for item in content:
                        if isinstance(item, dict):
                            if item.get("type") == "text":
                                text_parts.append(item.get("text", ""))
                            elif item.get("type") == "image":
                                text_parts.append(f"[Image: {item.get('mimeType', 'image')}]")
                            elif item.get("type") == "resource":
                                text_parts.append(f"[Resource: {item.get('uri', '')}]")
                        elif isinstance(item, str):
                            text_parts.append(item)

                    return ToolResult(output="\n".join(text_parts))

                # Fallback to string representation
                return ToolResult(output=str(result))

            return ToolResult(output=str(result))

        except Exception as e:
            return ToolResult(error=f"MCP tool error: {str(e)}")


def create_mcp_tools_from_server(server_name: str) -> list[MCPToolWrapper]:
    """
    Create tool wrappers for all tools from a specific server.

    Args:
        server_name: Name of the MCP server

    Returns:
        List of MCPToolWrapper instances
    """
    import asyncio

    registry = get_mcp_registry()
    client = registry.get_client(server_name)

    if not client or not client.is_running:
        return []

    # Get tools synchronously
    loop = asyncio.get_event_loop()
    if loop.is_running():
        # Create a new loop for this thread
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(
                lambda: asyncio.run(client.list_tools())
            )
            mcp_tools = future.result(timeout=10)
    else:
        mcp_tools = loop.run_until_complete(client.list_tools())

    return [MCPToolWrapper(tool) for tool in mcp_tools]


async def create_all_mcp_tools() -> list[MCPToolWrapper]:
    """
    Create tool wrappers for all tools from all running servers.

    Returns:
        List of MCPToolWrapper instances
    """
    registry = get_mcp_registry()
    all_tools = await registry.list_all_tools()

    return [MCPToolWrapper(tool) for tool in all_tools]


def get_mcp_tool_by_name(name: str) -> MCPToolWrapper | None:
    """
    Get an MCP tool wrapper by its full name.

    Args:
        name: Full tool name (mcp_{server}_{tool})

    Returns:
        MCPToolWrapper or None
    """
    if not name.startswith("mcp_"):
        return None

    # Parse server and tool name
    parts = name[4:].split("_", 1)
    if len(parts) != 2:
        return None

    server_name, tool_name = parts

    registry = get_mcp_registry()
    client = registry.get_client(server_name)

    if not client or not client.is_running:
        return None

    # Find the tool
    import asyncio
    loop = asyncio.get_event_loop()

    if loop.is_running():
        # Can't await in sync context
        return None

    tools = loop.run_until_complete(client.list_tools())

    for tool in tools:
        if tool.name == tool_name:
            return MCPToolWrapper(tool)

    return None
