"""
Computer Registry implementation.

Manages registration, discovery, and health monitoring of computers.
"""

import asyncio
import json
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Callable

from .types import (
    Computer,
    ComputerCapability,
    ComputerStatus,
    ComputerHealth,
)


# Type for health check callbacks
HealthCheckCallback = Callable[[Computer], bool]


class ComputerRegistry:
    """
    Central registry for all computers in the network.

    Features:
    - Register/unregister computers
    - Health monitoring
    - Capability-based lookup
    - Auto-cleanup of stale entries
    """

    def __init__(
        self,
        data_dir: Path | None = None,
        health_check_interval: float = 30.0,
        stale_threshold: float = 120.0,
    ):
        self._data_dir = data_dir or Path.home() / ".proto" / "registry"
        self._health_check_interval = health_check_interval
        self._stale_threshold = stale_threshold

        self._computers: dict[str, Computer] = {}
        self._lock = threading.Lock()
        self._health_task: asyncio.Task | None = None
        self._running = False

        # Callbacks
        self._on_register: list[Callable[[Computer], None]] = []
        self._on_unregister: list[Callable[[str], None]] = []
        self._on_status_change: list[Callable[[Computer, ComputerStatus], None]] = []

        # Ensure data directory exists
        self._data_dir.mkdir(parents=True, exist_ok=True)

        # Load persisted data
        self._load()

    def _load(self) -> None:
        """Load registry from disk."""
        registry_file = self._data_dir / "registry.json"
        if registry_file.exists():
            try:
                with open(registry_file, "r") as f:
                    data = json.load(f)

                for computer_data in data.get("computers", []):
                    computer = Computer.from_dict(computer_data)
                    # Mark as offline since we just loaded
                    computer.status = ComputerStatus.OFFLINE
                    self._computers[computer.id] = computer
            except Exception:
                pass

    def _save(self) -> None:
        """Save registry to disk."""
        registry_file = self._data_dir / "registry.json"
        data = {
            "computers": [c.to_dict() for c in self._computers.values()],
            "updated_at": datetime.utcnow().isoformat(),
        }

        with open(registry_file, "w") as f:
            json.dump(data, f, indent=2)

    async def start(self) -> None:
        """Start the registry (health monitoring)."""
        self._running = True
        self._health_task = asyncio.create_task(self._health_check_loop())
        print("[Registry] Started")

    async def stop(self) -> None:
        """Stop the registry."""
        self._running = False

        if self._health_task:
            self._health_task.cancel()
            try:
                await self._health_task
            except asyncio.CancelledError:
                pass

        self._save()
        print("[Registry] Stopped")

    async def register(self, computer: Computer) -> None:
        """Register a computer."""
        with self._lock:
            computer.registered_at = datetime.utcnow()
            computer.last_seen = datetime.utcnow()
            computer.status = ComputerStatus.ONLINE
            self._computers[computer.id] = computer
            self._save()

        print(f"[Registry] Registered: {computer.name} ({computer.id})")

        # Notify callbacks
        for callback in self._on_register:
            try:
                callback(computer)
            except Exception:
                pass

    async def unregister(self, computer_id: str) -> bool:
        """Unregister a computer."""
        with self._lock:
            computer = self._computers.pop(computer_id, None)
            if computer:
                self._save()

        if computer:
            print(f"[Registry] Unregistered: {computer.name} ({computer_id})")
            for callback in self._on_unregister:
                try:
                    callback(computer_id)
                except Exception:
                    pass
            return True

        return False

    async def heartbeat(self, computer_id: str, health: ComputerHealth | None = None) -> bool:
        """
        Update heartbeat for a computer.

        Args:
            computer_id: Computer ID
            health: Optional health update

        Returns:
            True if computer exists
        """
        with self._lock:
            computer = self._computers.get(computer_id)
            if not computer:
                return False

            computer.last_seen = datetime.utcnow()

            if health:
                computer.health = health

            # Update status based on health
            old_status = computer.status
            if health and not health.is_healthy():
                computer.status = ComputerStatus.ERROR
            elif computer.current_tasks >= computer.max_concurrent_tasks:
                computer.status = ComputerStatus.BUSY
            else:
                computer.status = ComputerStatus.ONLINE

            # Notify on status change
            if old_status != computer.status:
                for callback in self._on_status_change:
                    try:
                        callback(computer, old_status)
                    except Exception:
                        pass

        return True

    def get(self, computer_id: str) -> Computer | None:
        """Get a computer by ID."""
        return self._computers.get(computer_id)

    def list_all(self) -> list[Computer]:
        """List all registered computers."""
        return list(self._computers.values())

    def list_online(self) -> list[Computer]:
        """List all online computers."""
        return [
            c for c in self._computers.values()
            if c.status == ComputerStatus.ONLINE
        ]

    def list_available(self) -> list[Computer]:
        """List computers that can accept tasks."""
        return [c for c in self._computers.values() if c.can_accept_task()]

    def find_by_capability(
        self,
        capability: ComputerCapability,
        available_only: bool = True,
    ) -> list[Computer]:
        """Find computers with a specific capability."""
        computers = self._computers.values()

        if available_only:
            computers = [c for c in computers if c.can_accept_task()]

        return [c for c in computers if c.has_capability(capability)]

    def find_by_capabilities(
        self,
        capabilities: list[ComputerCapability],
        require_all: bool = True,
        available_only: bool = True,
    ) -> list[Computer]:
        """
        Find computers with specified capabilities.

        Args:
            capabilities: Required capabilities
            require_all: If True, computer must have all capabilities
            available_only: Only return available computers

        Returns:
            Matching computers sorted by load
        """
        computers = self._computers.values()

        if available_only:
            computers = [c for c in computers if c.can_accept_task()]

        if require_all:
            computers = [c for c in computers if c.has_all_capabilities(capabilities)]
        else:
            computers = [c for c in computers if c.has_any_capability(capabilities)]

        # Sort by current load
        return sorted(computers, key=lambda c: c.current_tasks)

    def find_by_tag(self, tag: str, available_only: bool = True) -> list[Computer]:
        """Find computers with a specific tag."""
        computers = self._computers.values()

        if available_only:
            computers = [c for c in computers if c.can_accept_task()]

        return [c for c in computers if tag in c.tags]

    def find_best_for_task(
        self,
        required_capabilities: list[ComputerCapability] | None = None,
        preferred_tags: list[str] | None = None,
    ) -> Computer | None:
        """
        Find the best computer for a task.

        Selection criteria:
        1. Has all required capabilities
        2. Prefers computers with matching tags
        3. Lowest current load
        4. Best health

        Args:
            required_capabilities: Capabilities needed for the task
            preferred_tags: Preferred tags (bonus points)

        Returns:
            Best matching computer or None
        """
        candidates = [c for c in self._computers.values() if c.can_accept_task()]

        if not candidates:
            return None

        # Filter by required capabilities
        if required_capabilities:
            candidates = [
                c for c in candidates
                if c.has_all_capabilities(required_capabilities)
            ]

        if not candidates:
            return None

        # Score each candidate
        def score(computer: Computer) -> float:
            s = 100.0

            # Lower load is better
            load_ratio = computer.current_tasks / max(computer.max_concurrent_tasks, 1)
            s -= load_ratio * 30

            # Better health is better
            if computer.health.is_healthy():
                s += 20
            else:
                s -= computer.health.error_count * 5

            # Lower latency is better
            s -= min(computer.health.latency_ms / 100, 20)

            # Preferred tags bonus
            if preferred_tags:
                matching_tags = sum(1 for t in preferred_tags if t in computer.tags)
                s += matching_tags * 10

            # Higher success rate is better
            s += computer.metrics.success_rate * 10

            return s

        candidates.sort(key=score, reverse=True)
        return candidates[0]

    async def update_task_count(self, computer_id: str, delta: int) -> bool:
        """Update the current task count for a computer."""
        with self._lock:
            computer = self._computers.get(computer_id)
            if not computer:
                return False

            computer.current_tasks = max(0, computer.current_tasks + delta)
            computer.health.active_tasks = computer.current_tasks

            # Update status
            old_status = computer.status
            if computer.current_tasks >= computer.max_concurrent_tasks:
                computer.status = ComputerStatus.BUSY
            elif computer.status == ComputerStatus.BUSY:
                computer.status = ComputerStatus.ONLINE

            if old_status != computer.status:
                for callback in self._on_status_change:
                    try:
                        callback(computer, old_status)
                    except Exception:
                        pass

        return True

    async def record_task_result(
        self,
        computer_id: str,
        success: bool,
        duration: float,
    ) -> None:
        """Record a task result for metrics."""
        with self._lock:
            computer = self._computers.get(computer_id)
            if not computer:
                return

            if success:
                computer.metrics.tasks_completed += 1
            else:
                computer.metrics.tasks_failed += 1

            # Update average duration (exponential moving average)
            alpha = 0.2
            computer.metrics.avg_task_duration = (
                alpha * duration +
                (1 - alpha) * computer.metrics.avg_task_duration
            )

            # Update success rate
            total = computer.metrics.tasks_completed + computer.metrics.tasks_failed
            if total > 0:
                computer.metrics.success_rate = (
                    computer.metrics.tasks_completed / total
                )

            computer.metrics.updated_at = datetime.utcnow()

    async def _health_check_loop(self) -> None:
        """Background loop for health checking."""
        while self._running:
            try:
                await asyncio.sleep(self._health_check_interval)
                await self._check_stale_computers()
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"[Registry] Health check error: {e}")

    async def _check_stale_computers(self) -> None:
        """Check for and mark stale computers."""
        threshold = datetime.utcnow() - timedelta(seconds=self._stale_threshold)

        with self._lock:
            for computer in self._computers.values():
                if computer.status == ComputerStatus.OFFLINE:
                    continue

                if computer.last_seen < threshold:
                    old_status = computer.status
                    computer.status = ComputerStatus.OFFLINE
                    print(f"[Registry] Marked stale: {computer.name}")

                    for callback in self._on_status_change:
                        try:
                            callback(computer, old_status)
                        except Exception:
                            pass

    def on_register(self, callback: Callable[[Computer], None]) -> None:
        """Register callback for new computer registration."""
        self._on_register.append(callback)

    def on_unregister(self, callback: Callable[[str], None]) -> None:
        """Register callback for computer unregistration."""
        self._on_unregister.append(callback)

    def on_status_change(
        self,
        callback: Callable[[Computer, ComputerStatus], None],
    ) -> None:
        """Register callback for status changes."""
        self._on_status_change.append(callback)

    def get_stats(self) -> dict[str, Any]:
        """Get registry statistics."""
        computers = list(self._computers.values())
        online = [c for c in computers if c.status == ComputerStatus.ONLINE]
        available = [c for c in computers if c.can_accept_task()]

        total_tasks = sum(c.current_tasks for c in computers)
        total_capacity = sum(c.max_concurrent_tasks for c in computers)

        return {
            "total_computers": len(computers),
            "online_computers": len(online),
            "available_computers": len(available),
            "total_active_tasks": total_tasks,
            "total_capacity": total_capacity,
            "utilization": total_tasks / max(total_capacity, 1),
            "computers_by_status": {
                status.value: len([c for c in computers if c.status == status])
                for status in ComputerStatus
            },
        }


# Global registry instance
_global_registry: ComputerRegistry | None = None


def get_computer_registry() -> ComputerRegistry:
    """Get or create the global computer registry."""
    global _global_registry

    if _global_registry is None:
        _global_registry = ComputerRegistry()

    return _global_registry


async def shutdown_registry() -> None:
    """Shutdown the global registry."""
    global _global_registry

    if _global_registry:
        await _global_registry.stop()
        _global_registry = None
