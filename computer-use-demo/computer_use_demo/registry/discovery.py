"""
Computer Discovery mechanisms.

Supports multiple discovery methods:
- Manual configuration
- Broadcast/multicast
- Service registry (Consul, etcd)
- Cloud provider APIs
"""

import asyncio
import json
from abc import ABC, abstractmethod
from enum import Enum
from pathlib import Path
from typing import Any

from .types import Computer, ComputerCapability, ComputerStatus


class DiscoveryMethod(str, Enum):
    """Methods for discovering computers."""

    MANUAL = "manual"
    BROADCAST = "broadcast"
    CONSUL = "consul"
    ETCD = "etcd"
    KUBERNETES = "kubernetes"
    FILE = "file"


class ComputerDiscoveryBackend(ABC):
    """Base class for discovery backends."""

    @abstractmethod
    async def discover(self) -> list[Computer]:
        """Discover computers using this backend."""
        pass


class ManualDiscoveryBackend(ComputerDiscoveryBackend):
    """Manual/static computer configuration."""

    def __init__(self, computers: list[Computer] | None = None):
        self._computers = computers or []

    def add(self, computer: Computer) -> None:
        """Add a computer to the manual list."""
        self._computers.append(computer)

    def remove(self, computer_id: str) -> bool:
        """Remove a computer from the manual list."""
        for i, c in enumerate(self._computers):
            if c.id == computer_id:
                self._computers.pop(i)
                return True
        return False

    async def discover(self) -> list[Computer]:
        """Return manually configured computers."""
        return self._computers.copy()


class FileDiscoveryBackend(ComputerDiscoveryBackend):
    """Discover computers from a JSON file."""

    def __init__(self, config_path: Path | None = None):
        self._config_path = config_path or Path.home() / ".proto" / "computers.json"

    async def discover(self) -> list[Computer]:
        """Load computers from config file."""
        if not self._config_path.exists():
            return []

        try:
            with open(self._config_path, "r") as f:
                data = json.load(f)

            computers = []
            for entry in data.get("computers", []):
                computer = Computer(
                    id=entry["id"],
                    name=entry["name"],
                    host=entry.get("host"),
                    port=entry.get("port"),
                    capabilities=[
                        ComputerCapability(c)
                        for c in entry.get("capabilities", [])
                    ],
                    tags=entry.get("tags", []),
                    metadata=entry.get("metadata", {}),
                    api_key=entry.get("api_key"),
                    max_concurrent_tasks=entry.get("max_concurrent_tasks", 5),
                )
                computers.append(computer)

            return computers

        except Exception as e:
            print(f"[Discovery] Failed to load from file: {e}")
            return []


class BroadcastDiscoveryBackend(ComputerDiscoveryBackend):
    """Discover computers via UDP broadcast."""

    def __init__(
        self,
        port: int = 9999,
        timeout: float = 5.0,
    ):
        self._port = port
        self._timeout = timeout

    async def discover(self) -> list[Computer]:
        """
        Send broadcast and collect responses.

        Note: This is a simplified implementation.
        Production would need proper socket handling.
        """
        computers = []

        try:
            # Create UDP socket
            loop = asyncio.get_event_loop()

            # This is a placeholder - real implementation would:
            # 1. Create UDP broadcast socket
            # 2. Send discovery packet
            # 3. Collect responses with timeout
            # 4. Parse responses into Computer objects

            print(f"[Discovery] Broadcast discovery on port {self._port}")
            print("[Discovery] (Not implemented - would send UDP broadcast)")

        except Exception as e:
            print(f"[Discovery] Broadcast failed: {e}")

        return computers


class ConsulDiscoveryBackend(ComputerDiscoveryBackend):
    """Discover computers from Consul service registry."""

    def __init__(
        self,
        consul_host: str = "localhost",
        consul_port: int = 8500,
        service_name: str = "proto-computer",
    ):
        self._host = consul_host
        self._port = consul_port
        self._service_name = service_name

    async def discover(self) -> list[Computer]:
        """Query Consul for registered computers."""
        computers = []

        try:
            # This would use the Consul HTTP API
            # GET /v1/catalog/service/{service_name}
            print(f"[Discovery] Consul discovery at {self._host}:{self._port}")
            print("[Discovery] (Not implemented - would query Consul API)")

        except Exception as e:
            print(f"[Discovery] Consul query failed: {e}")

        return computers


class ComputerDiscovery:
    """
    Manages computer discovery across multiple backends.
    """

    def __init__(self):
        self._backends: dict[DiscoveryMethod, ComputerDiscoveryBackend] = {}
        self._discovered: dict[str, Computer] = {}

        # Add default file backend
        self._backends[DiscoveryMethod.FILE] = FileDiscoveryBackend()
        self._backends[DiscoveryMethod.MANUAL] = ManualDiscoveryBackend()

    def add_backend(
        self,
        method: DiscoveryMethod,
        backend: ComputerDiscoveryBackend,
    ) -> None:
        """Add a discovery backend."""
        self._backends[method] = backend

    def remove_backend(self, method: DiscoveryMethod) -> None:
        """Remove a discovery backend."""
        self._backends.pop(method, None)

    async def discover(
        self,
        methods: list[DiscoveryMethod] | None = None,
    ) -> list[Computer]:
        """
        Run discovery across configured backends.

        Args:
            methods: Specific methods to use (or all if None)

        Returns:
            List of discovered computers
        """
        self._discovered.clear()

        backends_to_use = (
            [self._backends[m] for m in methods if m in self._backends]
            if methods
            else list(self._backends.values())
        )

        # Run discovery in parallel
        tasks = [b.discover() for b in backends_to_use]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Merge results (later discoveries override earlier)
        for result in results:
            if isinstance(result, Exception):
                print(f"[Discovery] Backend error: {result}")
                continue

            for computer in result:
                self._discovered[computer.id] = computer

        return list(self._discovered.values())

    async def discover_one(self, computer_id: str) -> Computer | None:
        """Try to discover a specific computer."""
        await self.discover()
        return self._discovered.get(computer_id)

    def get_discovered(self) -> list[Computer]:
        """Get last discovery results."""
        return list(self._discovered.values())

    def add_manual(self, computer: Computer) -> None:
        """Add a computer to manual discovery."""
        backend = self._backends.get(DiscoveryMethod.MANUAL)
        if isinstance(backend, ManualDiscoveryBackend):
            backend.add(computer)

    def save_to_file(self, path: Path | None = None) -> None:
        """Save discovered computers to file."""
        path = path or Path.home() / ".proto" / "computers.json"
        path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "computers": [
                {
                    "id": c.id,
                    "name": c.name,
                    "host": c.host,
                    "port": c.port,
                    "capabilities": [cap.value for cap in c.capabilities],
                    "tags": c.tags,
                    "metadata": c.metadata,
                    "max_concurrent_tasks": c.max_concurrent_tasks,
                }
                for c in self._discovered.values()
            ]
        }

        with open(path, "w") as f:
            json.dump(data, f, indent=2)

        print(f"[Discovery] Saved {len(self._discovered)} computers to {path}")
