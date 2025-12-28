"""
Computer registry for managing remote computer connections.

Stores computer configurations (name, host, SSH key, VNC port, etc.) in JSON file.
Provides CRUD operations and status monitoring.
"""

import asyncio
import json
import uuid
import logging
from dataclasses import dataclass, asdict, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import platform

logger = logging.getLogger(__name__)


@dataclass
class ComputerConfig:
    """Configuration for a computer in the network."""

    id: str
    name: str
    type: str  # 'local' or 'remote'
    host: Optional[str] = None  # Hostname/IP for remote computers
    port: int = 22  # SSH port
    username: Optional[str] = None
    ssh_key_path: Optional[str] = None  # Path to SSH private key
    vnc_port: int = 6080  # noVNC proxy port on remote
    api_port: int = 8000  # FastAPI port on remote
    status: str = "unknown"  # 'online', 'offline', 'error'
    platform_type: str = field(default_factory=lambda: platform.system())  # 'Darwin', 'Linux', 'Windows'
    last_check: Optional[str] = None  # ISO timestamp of last status check
    error_msg: Optional[str] = None  # Error message if status is 'error'

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)

    @staticmethod
    def from_dict(data: dict) -> "ComputerConfig":
        """Create from dictionary."""
        return ComputerConfig(**data)


class ComputerRegistry:
    """Manages computer registry stored in ~/.proto/computers.json"""

    def __init__(self, config_dir: Optional[str] = None):
        """
        Initialize registry.

        Args:
            config_dir: Directory to store computers.json (defaults to ~/.proto)
        """
        if config_dir is None:
            config_dir = str(Path.home() / ".proto")

        self.config_dir = Path(config_dir)
        self.config_file = self.config_dir / "computers.json"
        self.computers: Dict[str, ComputerConfig] = {}

        # Create directory if needed
        self.config_dir.mkdir(parents=True, exist_ok=True)

        # Load existing computers
        self._load()

        # Add local computer if not present
        self._ensure_local_computer()

        # Status monitoring task
        self._monitor_task: Optional[asyncio.Task] = None

    def _ensure_local_computer(self) -> None:
        """Ensure local computer is registered."""
        if "local" not in self.computers:
            local = ComputerConfig(
                id="local",
                name="This Computer",
                type="local",
                status="online",
                platform_type=platform.system(),
            )
            self.computers["local"] = local
            self._save()

    def _load(self) -> None:
        """Load computers from JSON file."""
        if self.config_file.exists():
            try:
                with open(self.config_file, "r") as f:
                    data = json.load(f)
                    for item in data.get("computers", []):
                        config = ComputerConfig.from_dict(item)
                        self.computers[config.id] = config
                logger.info(f"Loaded {len(self.computers)} computers from registry")
            except Exception as e:
                logger.error(f"Failed to load computer registry: {e}")

    def _save(self) -> None:
        """Save computers to JSON file."""
        try:
            data = {
                "version": 1,
                "last_updated": datetime.now().isoformat(),
                "computers": [c.to_dict() for c in self.computers.values()],
            }
            with open(self.config_file, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save computer registry: {e}")

    def add(self, computer: ComputerConfig) -> ComputerConfig:
        """Add a new computer to the registry."""
        if not computer.id:
            computer.id = str(uuid.uuid4())

        # Validate remote computer config
        if computer.type == "remote":
            if not computer.host:
                raise ValueError("Remote computer must have a host")
            if not computer.username:
                raise ValueError("Remote computer must have a username")

        self.computers[computer.id] = computer
        self._save()
        logger.info(f"Added computer: {computer.name} ({computer.id})")
        return computer

    def get(self, computer_id: str) -> Optional[ComputerConfig]:
        """Get a computer by ID."""
        return self.computers.get(computer_id)

    def list(self) -> List[ComputerConfig]:
        """List all computers."""
        return list(self.computers.values())

    def update(self, computer_id: str, updates: dict) -> Optional[ComputerConfig]:
        """Update a computer's configuration."""
        computer = self.computers.get(computer_id)
        if not computer:
            return None

        # Update fields
        for key, value in updates.items():
            if hasattr(computer, key):
                setattr(computer, key, value)

        self._save()
        logger.info(f"Updated computer: {computer.name}")
        return computer

    def delete(self, computer_id: str) -> bool:
        """Delete a computer from the registry."""
        if computer_id == "local":
            logger.warning("Cannot delete local computer")
            return False

        if computer_id in self.computers:
            computer = self.computers.pop(computer_id)
            self._save()
            logger.info(f"Deleted computer: {computer.name}")
            return True

        return False

    def set_status(
        self, computer_id: str, status: str, error_msg: Optional[str] = None
    ) -> None:
        """Update computer status."""
        computer = self.computers.get(computer_id)
        if computer:
            computer.status = status
            computer.error_msg = error_msg
            computer.last_check = datetime.now().isoformat()
            self._save()

    async def start_monitoring(self, check_interval: int = 30) -> None:
        """Start background status monitoring."""
        if self._monitor_task and not self._monitor_task.done():
            logger.warning("Monitoring already running")
            return

        async def monitor_loop():
            while True:
                try:
                    await self._check_all_statuses()
                    await asyncio.sleep(check_interval)
                except Exception as e:
                    logger.error(f"Error in monitoring loop: {e}")
                    await asyncio.sleep(check_interval)

        self._monitor_task = asyncio.create_task(monitor_loop())
        logger.info("Started computer status monitoring")

    async def stop_monitoring(self) -> None:
        """Stop background status monitoring."""
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
            self._monitor_task = None
            logger.info("Stopped computer status monitoring")

    async def _check_all_statuses(self) -> None:
        """Check status of all remote computers."""
        # Import here to avoid circular imports
        from .ssh_manager import SSHManager

        ssh_manager = SSHManager()

        for computer in self.computers.values():
            if computer.type == "local":
                self.set_status(computer.id, "online")
            else:
                try:
                    # Try to connect via SSH
                    async with ssh_manager.get_connection(computer) as conn:
                        if conn:
                            self.set_status(computer.id, "online")
                        else:
                            self.set_status(computer.id, "offline", "Connection failed")
                except Exception as e:
                    self.set_status(computer.id, "offline", str(e))
