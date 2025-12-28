"""
Remote computer tool that proxies tool calls to remote machines via SSH and REST API.

This tool executes computer actions on a remote computer by:
1. Using SSH to create an HTTP connection to the remote computer's API
2. POSTing tool calls to /api/remote/execute on the remote computer
3. Returning the ToolResult from the remote execution
"""

import asyncio
import json
from typing import Any, Literal

from ..tools.base import BaseAnthropicTool, ToolResult
from .ssh_manager import SSHManager
from .computer_registry import ComputerConfig


class RemoteComputerTool(BaseAnthropicTool):
    """
    Proxies computer tool calls to a remote machine via SSH and REST API.

    Uses SSH connection to securely communicate with the remote computer's API,
    then executes tool calls on the remote machine and returns the results.
    """

    name = "computer"
    api_type: Literal["computer_20250124"] = "computer_20250124"

    def __init__(
        self,
        computer_id: str,
        ssh_manager: SSHManager,
        computer_config: ComputerConfig,
    ):
        """
        Initialize remote computer tool.

        Args:
            computer_id: ID of the target computer
            ssh_manager: SSHManager instance for SSH connections
            computer_config: ComputerConfig with connection details
        """
        super().__init__()
        self.computer_id = computer_id
        self.ssh_manager = ssh_manager
        self.computer_config = computer_config

        # These will be fetched from remote on first call
        self.display_width = 1280
        self.display_height = 720

    @property
    def options(self):
        """Return tool options (display dimensions, etc.)."""
        return {
            "display_width_px": self.display_width,
            "display_height_px": self.display_height,
            "display_number": None,
        }

    def to_params(self):
        """Convert tool to API parameters."""
        return {
            "name": self.name,
            "type": self.api_type,
            **self.options,
        }

    async def __call__(self, **kwargs) -> Any:
        """
        Execute tool call on remote computer.

        Args:
            action: Action type (screenshot, mouse_move, click, type_text, scroll, key)
            **kwargs: Action-specific parameters

        Returns:
            ToolResult with screenshot, output, or error
        """
        action = kwargs.get("action")

        if not action:
            return ToolResult(error="Action not specified")

        try:
            # Execute on remote computer via SSH tunnel
            result = await self._execute_remote_action(action, kwargs)
            return result

        except Exception as e:
            import traceback
            return ToolResult(error=f"Remote tool execution failed: {e}\n{traceback.format_exc()}")

    async def _execute_remote_action(self, action: str, params: dict) -> ToolResult:
        """
        Execute an action on the remote computer.

        Args:
            action: Action type
            params: Action parameters

        Returns:
            ToolResult from remote execution
        """
        try:
            # Use SSH connection to reach remote API
            async with self.ssh_manager.get_connection(self.computer_config) as ssh_conn:
                # Execute HTTP request to remote API
                # In a real implementation, we'd use SSH tunneling to forward the API port
                # For now, we'll assume the remote API is accessible via SSH tunnel

                # Create HTTP client that goes through SSH
                api_url = f"http://localhost:{self.computer_config.api_port}/api/remote/execute"

                # Build the request
                request_data = {
                    "action": action,
                    **{k: v for k, v in params.items() if k != "action"},
                }

                # Execute command on remote to make the API call
                # This is a simplified approach - a better approach would use SSH tunneling
                command = f'curl -X POST "{api_url}" -H "Content-Type: application/json" -d \'{json.dumps(request_data)}\' 2>/dev/null'

                exit_code, stdout, stderr = await ssh_conn.execute_command(command)

                if exit_code != 0:
                    return ToolResult(error=f"Remote API call failed: {stderr}")

                # Parse response
                try:
                    response_data = json.loads(stdout)

                    # Reconstruct ToolResult
                    result = ToolResult(
                        output=response_data.get("output"),
                        error=response_data.get("error"),
                        base64_image=response_data.get("base64_image"),
                        system=response_data.get("system"),
                    )

                    # Update display dimensions if provided
                    if "display_width" in response_data:
                        self.display_width = response_data["display_width"]
                    if "display_height" in response_data:
                        self.display_height = response_data["display_height"]

                    return result

                except json.JSONDecodeError as e:
                    return ToolResult(error=f"Failed to parse remote response: {e}\nResponse: {stdout}")

        except Exception as e:
            import traceback
            return ToolResult(error=f"SSH execution failed: {e}\n{traceback.format_exc()}")
