"""
VNC tunnel management via SSH port forwarding.

Manages SSH tunnels for VNC connections, allowing local access to remote noVNC servers.
Each tunnel forwards a local port to the remote noVNC server (typically port 6080).
"""

import asyncio
import socket
import logging
from typing import Dict, Optional
from pathlib import Path

from .ssh_manager import SSHManager
from .computer_registry import ComputerRegistry, ComputerConfig

logger = logging.getLogger(__name__)


class VNCTunnel:
    """Manages SSH tunnels for VNC connections."""

    def __init__(self, registry: ComputerRegistry, ssh_manager: SSHManager):
        """
        Initialize VNC tunnel manager.

        Args:
            registry: ComputerRegistry instance
            ssh_manager: SSHManager instance for SSH connections
        """
        self.registry = registry
        self.ssh_manager = ssh_manager
        self.tunnels: Dict[str, int] = {}  # computer_id -> local_port
        self._tunnel_processes: Dict[str, asyncio.subprocess.Process] = {}

    def _find_free_port(self, start_port: int = 6080) -> int:
        """
        Find an available local port.

        Args:
            start_port: Starting port to search from

        Returns:
            Available port number
        """
        port = start_port
        while port < 65535:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.bind(("127.0.0.1", port))
                sock.close()
                return port
            except OSError:
                port += 1

        raise RuntimeError("Could not find available port for VNC tunnel")

    async def create_tunnel(self, computer_id: str) -> Optional[int]:
        """
        Create SSH tunnel for a remote computer's VNC server.

        Creates a local port that forwards to remote_host:remote_port via SSH.
        Example: ssh -L 6080:localhost:6080 user@remote_host

        Args:
            computer_id: ID of the computer to create tunnel for

        Returns:
            Local port number for VNC access, or None if tunnel creation failed
        """
        # Check if tunnel already exists
        if computer_id in self.tunnels:
            return self.tunnels[computer_id]

        computer = self.registry.get(computer_id)
        if not computer:
            logger.error(f"Computer not found: {computer_id}")
            return None

        if computer.type == "local":
            # Local computer - no tunnel needed, VNC available on localhost:6080
            self.tunnels[computer_id] = computer.vnc_port
            return computer.vnc_port

        # Remote computer - create SSH tunnel
        try:
            local_port = self._find_free_port()

            # Find SSH key - try ed25519 first, then rsa
            ssh_key = computer.ssh_key_path
            if ssh_key:
                key_path = Path(ssh_key).expanduser()
                if not key_path.exists():
                    # Try alternative keys
                    for alt_key in ["~/.ssh/id_ed25519", "~/.ssh/id_rsa"]:
                        alt_path = Path(alt_key).expanduser()
                        if alt_path.exists():
                            ssh_key = str(alt_path)
                            break

            # Create SSH tunnel using subprocess
            # ssh -L local_port:localhost:remote_vnc_port user@host
            ssh_cmd = [
                "ssh",
                "-o", "StrictHostKeyChecking=no",
                "-o", "UserKnownHostsFile=/dev/null",
                "-o", "ConnectTimeout=10",
                "-L",
                f"{local_port}:localhost:{computer.vnc_port}",
                "-N",  # Don't execute command
                "-f",  # Go to background
                f"{computer.username}@{computer.host}",
            ]

            # Add key file if specified and exists
            if ssh_key and Path(ssh_key).expanduser().exists():
                ssh_cmd.insert(1, "-i")
                ssh_cmd.insert(2, ssh_key)

            # Execute SSH tunnel
            logger.info(f"Creating SSH tunnel: {' '.join(ssh_cmd)}")
            try:
                process = await asyncio.create_subprocess_exec(
                    *ssh_cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )

                # Wait a bit for tunnel to establish
                try:
                    stdout, stderr = await asyncio.wait_for(
                        process.communicate(), timeout=10
                    )
                    if process.returncode != 0:
                        error_msg = stderr.decode() if stderr else 'Unknown error'
                        logger.error(f"SSH tunnel creation failed (exit {process.returncode}): {error_msg}")
                        print(f"[VNC] SSH tunnel failed: {error_msg}")
                        return None
                except asyncio.TimeoutError:
                    # SSH tunnel with -f goes to background, so timeout is expected
                    logger.info("SSH tunnel started (backgrounded)")
                    pass

                self._tunnel_processes[computer_id] = process
                self.tunnels[computer_id] = local_port

                logger.info(
                    f"Created VNC tunnel for {computer.name}: localhost:{local_port} -> {computer.host}:{computer.vnc_port}"
                )
                print(f"[VNC] ✓ Tunnel created: localhost:{local_port} -> {computer.host}:{computer.vnc_port}")
                return local_port

            except Exception as e:
                logger.error(f"Failed to create SSH tunnel: {e}")
                print(f"[VNC] ✗ SSH tunnel error: {e}")
                return None

        except Exception as e:
            logger.error(f"Failed to create VNC tunnel for {computer_id}: {e}")
            return None

    async def close_tunnel(self, computer_id: str) -> bool:
        """
        Close VNC tunnel for a computer.

        Args:
            computer_id: ID of the computer

        Returns:
            True if tunnel was closed successfully
        """
        if computer_id not in self.tunnels:
            return False

        try:
            if computer_id in self._tunnel_processes:
                process = self._tunnel_processes[computer_id]
                process.terminate()
                try:
                    await asyncio.wait_for(process.wait(), timeout=5)
                except asyncio.TimeoutError:
                    process.kill()
                del self._tunnel_processes[computer_id]

            del self.tunnels[computer_id]
            logger.info(f"Closed VNC tunnel for {computer_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to close VNC tunnel for {computer_id}: {e}")
            return False

    async def get_vnc_url(self, computer_id: str, direct: bool = True) -> Optional[str]:
        """
        Get WebSocket URL for noVNC viewer.

        Args:
            computer_id: ID of the computer
            direct: If True, return direct URL to remote host (for public ports).
                   If False, create SSH tunnel and return localhost URL.

        Returns:
            WebSocket URL like ws://localhost:6080/websockify or ws://remote-ip:6080/websockify
        """
        computer = self.registry.get(computer_id)
        if not computer:
            logger.error(f"Computer not found: {computer_id}")
            return None

        # For local computer, always use localhost
        if computer.type == "local":
            return f"ws://localhost:{computer.vnc_port}/websockify"

        # For remote computers with direct mode (public ports), connect directly
        # Hetzner instances use nginx proxy on port 80 - VNC port 6080 is localhost only
        if direct and computer.host:
            # Connect directly to noVNC on port 6080
            logger.info(f"Using direct VNC connection to {computer.host}:6080")
            return f"http://{computer.host}:6080"

        # Fallback: create SSH tunnel
        local_port = await self.create_tunnel(computer_id)
        if not local_port:
            return None

        return f"ws://localhost:{local_port}/websockify"

    async def close_all_tunnels(self) -> None:
        """Close all active VNC tunnels."""
        computer_ids = list(self.tunnels.keys())
        for computer_id in computer_ids:
            await self.close_tunnel(computer_id)

        logger.info("Closed all VNC tunnels")
