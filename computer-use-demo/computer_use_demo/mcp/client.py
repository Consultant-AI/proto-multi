"""
MCP client implementation.

Communicates with MCP servers using JSON-RPC 2.0 over stdio.
"""

import asyncio
import json
import os
import subprocess
from typing import Any, AsyncIterator

from .types import (
    MCPPrompt,
    MCPRequest,
    MCPResource,
    MCPResponse,
    MCPServerConfig,
    MCPServerStatus,
    MCPTool,
)


class MCPClient:
    """
    Client for communicating with an MCP server.

    Uses JSON-RPC 2.0 over stdio (stdin/stdout).
    """

    def __init__(self, config: MCPServerConfig):
        self.config = config
        self._process: subprocess.Popen | None = None
        self._request_id = 0
        self._pending_requests: dict[int, asyncio.Future] = {}
        self._reader_task: asyncio.Task | None = None
        self._status = MCPServerStatus.STOPPED
        self._lock = asyncio.Lock()

    @property
    def status(self) -> MCPServerStatus:
        return self._status

    @property
    def is_running(self) -> bool:
        return self._status == MCPServerStatus.RUNNING

    async def start(self) -> bool:
        """
        Start the MCP server process.

        Returns:
            True if started successfully
        """
        async with self._lock:
            if self._status == MCPServerStatus.RUNNING:
                return True

            self._status = MCPServerStatus.STARTING

            try:
                # Build environment
                env = os.environ.copy()
                env.update(self.config.env)

                # Build command
                cmd = [self.config.command] + self.config.args

                # Start process
                self._process = subprocess.Popen(
                    cmd,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    env=env,
                    cwd=self.config.cwd,
                    text=True,
                    bufsize=1,  # Line buffered
                )

                # Start reader task
                self._reader_task = asyncio.create_task(self._read_responses())

                # Initialize the server
                await self._initialize()

                self._status = MCPServerStatus.RUNNING
                return True

            except Exception as e:
                self._status = MCPServerStatus.ERROR
                await self.stop()
                raise RuntimeError(f"Failed to start MCP server '{self.config.name}': {e}")

    async def stop(self) -> None:
        """Stop the MCP server process."""
        async with self._lock:
            self._status = MCPServerStatus.STOPPING

            # Cancel reader task
            if self._reader_task:
                self._reader_task.cancel()
                try:
                    await self._reader_task
                except asyncio.CancelledError:
                    pass
                self._reader_task = None

            # Terminate process
            if self._process:
                try:
                    self._process.terminate()
                    self._process.wait(timeout=5)
                except Exception:
                    try:
                        self._process.kill()
                    except Exception:
                        pass
                self._process = None

            # Cancel pending requests
            for future in self._pending_requests.values():
                future.cancel()
            self._pending_requests.clear()

            self._status = MCPServerStatus.STOPPED

    async def _initialize(self) -> None:
        """Initialize the MCP server connection."""
        # Send initialize request
        response = await self.request(
            "initialize",
            {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "roots": {"listChanged": True},
                    "sampling": {},
                },
                "clientInfo": {
                    "name": "proto-multi",
                    "version": "1.0.0",
                },
            },
        )

        if response.is_error:
            raise RuntimeError(f"Initialize failed: {response.error}")

        # Send initialized notification
        await self.notify("notifications/initialized", {})

    async def request(
        self,
        method: str,
        params: dict[str, Any] | None = None,
        timeout: float = 30.0,
    ) -> MCPResponse:
        """
        Send a request to the MCP server and wait for response.

        Args:
            method: JSON-RPC method name
            params: Method parameters
            timeout: Request timeout in seconds

        Returns:
            MCPResponse
        """
        if not self.is_running and self._status != MCPServerStatus.STARTING:
            raise RuntimeError("MCP server is not running")

        self._request_id += 1
        request_id = self._request_id

        # Create request
        request = {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": method,
        }
        if params:
            request["params"] = params

        # Create future for response
        future: asyncio.Future[MCPResponse] = asyncio.get_event_loop().create_future()
        self._pending_requests[request_id] = future

        try:
            # Send request
            await self._send(request)

            # Wait for response
            response = await asyncio.wait_for(future, timeout=timeout)
            return response

        except asyncio.TimeoutError:
            self._pending_requests.pop(request_id, None)
            return MCPResponse(error={"code": -32000, "message": "Request timeout"})

        except Exception as e:
            self._pending_requests.pop(request_id, None)
            return MCPResponse(error={"code": -32000, "message": str(e)})

    async def notify(
        self,
        method: str,
        params: dict[str, Any] | None = None,
    ) -> None:
        """
        Send a notification (no response expected).

        Args:
            method: JSON-RPC method name
            params: Method parameters
        """
        notification = {
            "jsonrpc": "2.0",
            "method": method,
        }
        if params:
            notification["params"] = params

        await self._send(notification)

    async def _send(self, message: dict[str, Any]) -> None:
        """Send a message to the server."""
        if not self._process or not self._process.stdin:
            raise RuntimeError("Process not running")

        content = json.dumps(message)
        # MCP uses Content-Length header like LSP
        header = f"Content-Length: {len(content)}\r\n\r\n"

        try:
            self._process.stdin.write(header + content)
            self._process.stdin.flush()
        except Exception as e:
            raise RuntimeError(f"Failed to send message: {e}")

    async def _read_responses(self) -> None:
        """Background task to read responses from server."""
        if not self._process or not self._process.stdout:
            return

        buffer = ""

        while True:
            try:
                # Read a line
                line = await asyncio.get_event_loop().run_in_executor(
                    None, self._process.stdout.readline
                )

                if not line:
                    # Process ended
                    break

                buffer += line

                # Check for complete message
                while "\r\n\r\n" in buffer:
                    header_end = buffer.index("\r\n\r\n")
                    header = buffer[:header_end]
                    buffer = buffer[header_end + 4:]

                    # Parse Content-Length
                    content_length = 0
                    for line in header.split("\r\n"):
                        if line.startswith("Content-Length:"):
                            content_length = int(line.split(":")[1].strip())
                            break

                    if content_length > 0:
                        # Read content
                        while len(buffer) < content_length:
                            more = await asyncio.get_event_loop().run_in_executor(
                                None, lambda: self._process.stdout.read(content_length - len(buffer))
                            )
                            if not more:
                                break
                            buffer += more

                        content = buffer[:content_length]
                        buffer = buffer[content_length:]

                        # Parse JSON
                        try:
                            message = json.loads(content)
                            await self._handle_message(message)
                        except json.JSONDecodeError:
                            pass

            except asyncio.CancelledError:
                break
            except Exception:
                break

    async def _handle_message(self, message: dict[str, Any]) -> None:
        """Handle an incoming message from the server."""
        # Check if it's a response
        if "id" in message and message["id"] is not None:
            request_id = message["id"]
            future = self._pending_requests.pop(request_id, None)

            if future and not future.done():
                response = MCPResponse(
                    result=message.get("result"),
                    error=message.get("error"),
                    id=request_id,
                )
                future.set_result(response)

        # Handle notifications (no id or id is null)
        # For now, we just log them
        elif "method" in message:
            # Server notification
            pass

    # High-level API methods

    async def list_tools(self) -> list[MCPTool]:
        """Get list of tools provided by this server."""
        response = await self.request("tools/list")

        if response.is_error:
            return []

        tools = []
        for tool_data in response.result.get("tools", []):
            tool = MCPTool(
                name=tool_data.get("name", ""),
                description=tool_data.get("description", ""),
                input_schema=tool_data.get("inputSchema", {}),
                server_name=self.config.name,
            )
            tools.append(tool)

        return tools

    async def call_tool(
        self,
        name: str,
        arguments: dict[str, Any] | None = None,
    ) -> Any:
        """
        Call a tool on the server.

        Args:
            name: Tool name
            arguments: Tool arguments

        Returns:
            Tool result
        """
        response = await self.request(
            "tools/call",
            {
                "name": name,
                "arguments": arguments or {},
            },
        )

        if response.is_error:
            raise RuntimeError(f"Tool call failed: {response.error}")

        return response.result

    async def list_resources(self) -> list[MCPResource]:
        """Get list of resources provided by this server."""
        response = await self.request("resources/list")

        if response.is_error:
            return []

        resources = []
        for res_data in response.result.get("resources", []):
            resource = MCPResource(
                uri=res_data.get("uri", ""),
                name=res_data.get("name", ""),
                description=res_data.get("description", ""),
                mime_type=res_data.get("mimeType", "text/plain"),
                server_name=self.config.name,
            )
            resources.append(resource)

        return resources

    async def read_resource(self, uri: str) -> Any:
        """Read a resource from the server."""
        response = await self.request("resources/read", {"uri": uri})

        if response.is_error:
            raise RuntimeError(f"Resource read failed: {response.error}")

        return response.result

    async def list_prompts(self) -> list[MCPPrompt]:
        """Get list of prompts provided by this server."""
        response = await self.request("prompts/list")

        if response.is_error:
            return []

        prompts = []
        for prompt_data in response.result.get("prompts", []):
            prompt = MCPPrompt(
                name=prompt_data.get("name", ""),
                description=prompt_data.get("description", ""),
                arguments=prompt_data.get("arguments", []),
                server_name=self.config.name,
            )
            prompts.append(prompt)

        return prompts

    async def get_prompt(
        self,
        name: str,
        arguments: dict[str, str] | None = None,
    ) -> Any:
        """Get a prompt with arguments filled in."""
        response = await self.request(
            "prompts/get",
            {
                "name": name,
                "arguments": arguments or {},
            },
        )

        if response.is_error:
            raise RuntimeError(f"Prompt get failed: {response.error}")

        return response.result
