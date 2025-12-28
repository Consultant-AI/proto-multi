"""
Remote computer control functionality.

Enables distributed multi-computer control via SSH tunneling and REST API.
"""

from .computer_registry import ComputerConfig, ComputerRegistry
from .ssh_manager import SSHManager, SSHConnection
from .remote_computer_tool import RemoteComputerTool
from .vnc_tunnel import VNCTunnel

__all__ = [
    "ComputerConfig",
    "ComputerRegistry",
    "SSHManager",
    "SSHConnection",
    "RemoteComputerTool",
    "VNCTunnel",
]
