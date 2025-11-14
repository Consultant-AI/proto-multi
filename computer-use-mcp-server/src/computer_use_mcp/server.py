"""
MCP Server that bridges Claude Code to the computer-use CLI tool.

This server acts as a bridge, forwarding Claude's requests to the computer-use CLI
and streaming back the logs and responses.
"""

import asyncio
import atexit
import os
import signal
import sys
from pathlib import Path
from typing import Optional

from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent

# Initialize FastMCP server
mcp = FastMCP("computer-use")

# Global subprocess handle
_cli_process: Optional[asyncio.subprocess.Process] = None
_cli_reader_task: Optional[asyncio.Task] = None
_cli_logs: list[str] = []


async def _read_cli_output():
    """Background task to read CLI output and store it in logs."""
    global _cli_process, _cli_logs

    if not _cli_process or not _cli_process.stdout:
        return

    try:
        while True:
            line = await _cli_process.stdout.readline()
            if not line:
                break

            decoded_line = line.decode("utf-8", errors="ignore").rstrip()
            _cli_logs.append(decoded_line)

            # Keep only last 100 lines to avoid memory issues
            if len(_cli_logs) > 100:
                _cli_logs.pop(0)
    except Exception as e:
        _cli_logs.append(f"[ERROR] Reading CLI output: {str(e)}")


async def _ensure_cli_running():
    """Ensure the computer-use CLI subprocess is running."""
    global _cli_process, _cli_reader_task

    # Check if process is already running
    if _cli_process and _cli_process.returncode is None:
        return True

    # Find the computer-use-demo directory
    # Assuming it's a sibling directory to computer-use-mcp-server
    mcp_dir = Path(__file__).parent.parent.parent
    demo_dir = mcp_dir.parent / "computer-use-demo"

    if not demo_dir.exists():
        raise RuntimeError(
            f"computer-use-demo directory not found at {demo_dir}. "
            "Please ensure it's in the same parent directory as computer-use-mcp-server."
        )

    # Get API key from environment
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError(
            "ANTHROPIC_API_KEY environment variable not set. "
            "Please set it before using the computer-use bridge."
        )

    # Start the CLI process
    try:
        # Try to find python3 first, fall back to python
        import shutil
        python_cmd = shutil.which("python3") or shutil.which("python")
        if not python_cmd:
            raise RuntimeError("Python executable not found in PATH")

        # Create process in new process group for better cleanup
        # This ensures child processes are killed when parent dies
        _cli_process = await asyncio.create_subprocess_exec(
            python_cmd,
            "-m",
            "computer_use_demo.cli",
            "--model",
            "claude-sonnet-4-5-20250929",
            "--tool-version",
            "computer_use_local",
            cwd=str(demo_dir),
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            env={**os.environ, "ANTHROPIC_API_KEY": api_key},
            start_new_session=True,  # Create new process group
        )

        # Start background task to read output
        _cli_reader_task = asyncio.create_task(_read_cli_output())

        # Wait for the CLI to be ready (look for "you>" prompt)
        max_wait = 10  # seconds
        start = asyncio.get_event_loop().time()
        while asyncio.get_event_loop().time() - start < max_wait:
            await asyncio.sleep(0.5)
            if _cli_logs and any("you>" in line for line in _cli_logs):
                return True
            # Check if process died
            if _cli_process.returncode is not None:
                raise RuntimeError(f"CLI exited during startup with code {_cli_process.returncode}")

        # If we get here, timeout waiting for prompt
        return True  # Continue anyway
    except Exception as e:
        raise RuntimeError(f"Failed to start computer-use CLI: {str(e)}")


async def _send_to_cli(prompt: str) -> str:
    """Send a prompt to the CLI and return the response."""
    global _cli_process, _cli_logs

    if not _cli_process or not _cli_process.stdin:
        raise RuntimeError("CLI process not running")

    # Don't clear logs - we want to see startup messages
    # Store the starting log count
    start_log_count = len(_cli_logs)

    # Send the prompt
    try:
        _cli_process.stdin.write(f"{prompt}\n".encode("utf-8"))
        await _cli_process.stdin.drain()
    except Exception as e:
        raise RuntimeError(f"Failed to send prompt to CLI: {str(e)}")

    # Wait for the response (look for the next "you>" prompt or timeout)
    timeout = 300  # 5 minutes
    start_time = asyncio.get_event_loop().time()

    while True:
        await asyncio.sleep(0.5)

        # Check timeout
        if asyncio.get_event_loop().time() - start_time > timeout:
            return "\n".join(_cli_logs) + "\n\n[TIMEOUT] Response took longer than 5 minutes."

        # Check if we have logs
        if len(_cli_logs) > start_log_count:
            last_line = _cli_logs[-1]

            # Look for the prompt indicating Claude is done
            if last_line.startswith("you>") or "you>" in last_line:
                # Return all logs except the last "you>" line
                return "\n".join(_cli_logs[:-1])

        # Check if process died
        if _cli_process.returncode is not None:
            error_msg = f"CLI process exited with code {_cli_process.returncode}"
            if _cli_logs:
                error_msg += f"\n\nLogs:\n" + "\n".join(_cli_logs)
            raise RuntimeError(error_msg)


@mcp.tool()
async def computer_use(prompt: str) -> list[TextContent]:
    """
    Hand off control to the computer-use agent with a natural language prompt.

    This tool bridges to the computer-use CLI, which gives Claude full computer control
    including screenshots, mouse control, keyboard input, and more.

    Args:
        prompt: Natural language instruction for the computer-use agent (e.g., "open chrome and search for cats")

    Returns:
        The full output from the computer-use agent, including all logs and responses

    Examples:
        - computer_use("take a screenshot and tell me what you see")
        - computer_use("open the calculator app and calculate 123 * 456")
        - computer_use("open chrome and navigate to github.com")
    """
    try:
        # Ensure CLI is running
        await _ensure_cli_running()

        # Send the prompt and get response
        response = await _send_to_cli(prompt)

        return [TextContent(type="text", text=response)]

    except Exception as e:
        error_msg = f"Error in computer_use: {str(e)}"
        if _cli_logs:
            error_msg += f"\n\nRecent logs:\n" + "\n".join(_cli_logs[-20:])

        return [TextContent(type="text", text=error_msg)]


@mcp.tool()
async def get_computer_use_logs(last_n_lines: int = 50) -> list[TextContent]:
    """
    Get recent logs from the computer-use agent.

    Useful for checking the status of the agent or debugging issues.

    Args:
        last_n_lines: Number of recent log lines to retrieve (default: 50)

    Returns:
        Recent log lines from the computer-use agent
    """
    global _cli_logs, _cli_process

    if not _cli_logs:
        if _cli_process and _cli_process.returncode is None:
            return [TextContent(type="text", text="Computer-use agent is running but no logs yet.")]
        else:
            return [TextContent(type="text", text="Computer-use agent is not running. Use the computer_use tool to start it.")]

    logs = _cli_logs[-last_n_lines:]
    return [TextContent(type="text", text="\n".join(logs))]


@mcp.tool()
async def stop_computer_use() -> list[TextContent]:
    """
    Stop the computer-use agent subprocess.

    Use this when you're done with computer control or want to restart the agent.

    Returns:
        Status message
    """
    global _cli_process, _cli_reader_task, _cli_logs

    if not _cli_process:
        return [TextContent(type="text", text="Computer-use agent is not running.")]

    try:
        # Send quit command
        if _cli_process.stdin:
            _cli_process.stdin.write(b":quit\n")
            await _cli_process.stdin.drain()

        # Wait for process to exit
        try:
            await asyncio.wait_for(_cli_process.wait(), timeout=5.0)
        except asyncio.TimeoutError:
            _cli_process.kill()
            await _cli_process.wait()

        # Cancel reader task
        if _cli_reader_task:
            _cli_reader_task.cancel()
            try:
                await _cli_reader_task
            except asyncio.CancelledError:
                pass

        _cli_process = None
        _cli_reader_task = None
        _cli_logs.clear()

        return [TextContent(type="text", text="Computer-use agent stopped successfully.")]

    except Exception as e:
        return [TextContent(type="text", text=f"Error stopping computer-use agent: {str(e)}")]


def _cleanup_cli_process():
    """Cleanup function to kill CLI process on exit."""
    global _cli_process, _cli_reader_task

    if _cli_process and _cli_process.returncode is None:
        try:
            # Send quit command first for graceful shutdown
            if _cli_process.stdin and not _cli_process.stdin.is_closing():
                try:
                    _cli_process.stdin.write(b":quit\n")
                    _cli_process.stdin.close()
                except:
                    pass

            # Kill the entire process group (handles orphaned children)
            import time
            pid = _cli_process.pid
            if pid:
                try:
                    # Kill process group (negative PID kills the group)
                    os.killpg(os.getpgid(pid), signal.SIGTERM)
                    time.sleep(0.5)

                    # Force kill if still alive
                    try:
                        os.killpg(os.getpgid(pid), signal.SIGKILL)
                    except ProcessLookupError:
                        pass  # Already dead
                except (ProcessLookupError, OSError):
                    # Process or group doesn't exist, try direct kill
                    try:
                        _cli_process.terminate()
                        time.sleep(0.5)
                        _cli_process.kill()
                    except:
                        pass

        except Exception:
            pass  # Process may already be dead

    # Cancel reader task if exists
    if _cli_reader_task and not _cli_reader_task.done():
        try:
            _cli_reader_task.cancel()
        except:
            pass


def _signal_handler(signum, frame):
    """Handle interrupt signals to cleanup properly."""
    _cleanup_cli_process()
    sys.exit(0)


def main():
    """Initialize and run the MCP server."""
    # Register cleanup handlers
    atexit.register(_cleanup_cli_process)
    signal.signal(signal.SIGINT, _signal_handler)
    signal.signal(signal.SIGTERM, _signal_handler)

    try:
        # Run the server with stdio transport (standard for MCP)
        mcp.run(transport='stdio')
    finally:
        # Ensure cleanup on exit
        _cleanup_cli_process()


if __name__ == "__main__":
    main()
