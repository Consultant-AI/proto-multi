"""
Type definitions for MCP (Model Context Protocol) integration.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class MCPServerStatus(str, Enum):
    """Status of an MCP server."""

    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    ERROR = "error"
    STOPPING = "stopping"


@dataclass
class MCPServerConfig:
    """Configuration for an MCP server."""

    # Server name (unique identifier)
    name: str

    # Command to start the server
    command: str

    # Arguments for the command
    args: list[str] = field(default_factory=list)

    # Environment variables
    env: dict[str, str] = field(default_factory=dict)

    # Working directory
    cwd: str | None = None

    # Whether to auto-start this server
    auto_start: bool = True

    # Timeout for server startup (seconds)
    startup_timeout: float = 30.0

    # Whether this server is enabled
    enabled: bool = True


@dataclass
class MCPTool:
    """A tool provided by an MCP server."""

    # Tool name
    name: str

    # Tool description
    description: str

    # Input schema (JSON Schema)
    input_schema: dict[str, Any] = field(default_factory=dict)

    # Server that provides this tool
    server_name: str = ""


@dataclass
class MCPResource:
    """A resource provided by an MCP server."""

    # Resource URI
    uri: str

    # Resource name
    name: str

    # Resource description
    description: str = ""

    # MIME type
    mime_type: str = "text/plain"

    # Server that provides this resource
    server_name: str = ""


@dataclass
class MCPPrompt:
    """A prompt template provided by an MCP server."""

    # Prompt name
    name: str

    # Prompt description
    description: str = ""

    # Arguments the prompt accepts
    arguments: list[dict[str, Any]] = field(default_factory=list)

    # Server that provides this prompt
    server_name: str = ""


@dataclass
class MCPServerInfo:
    """Information about a running MCP server."""

    # Server name
    name: str

    # Current status
    status: MCPServerStatus = MCPServerStatus.STOPPED

    # Process ID (if running)
    pid: int | None = None

    # Tools provided by this server
    tools: list[MCPTool] = field(default_factory=list)

    # Resources provided by this server
    resources: list[MCPResource] = field(default_factory=list)

    # Prompts provided by this server
    prompts: list[MCPPrompt] = field(default_factory=list)

    # Last error message (if status is ERROR)
    error: str | None = None

    # Server version
    version: str | None = None


@dataclass
class MCPRequest:
    """A JSON-RPC request to an MCP server."""

    method: str
    params: dict[str, Any] = field(default_factory=dict)
    id: int | str | None = None


@dataclass
class MCPResponse:
    """A JSON-RPC response from an MCP server."""

    result: Any = None
    error: dict[str, Any] | None = None
    id: int | str | None = None

    @property
    def is_error(self) -> bool:
        return self.error is not None
