"""
Type definitions for the Computer Registry.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class ComputerCapability(str, Enum):
    """Capabilities a computer can have."""

    # Execution capabilities
    CODE_EXECUTION = "code_execution"
    SHELL_ACCESS = "shell_access"
    FILE_SYSTEM = "file_system"

    # Browser/UI
    BROWSER = "browser"
    GUI = "gui"
    SCREENSHOT = "screenshot"

    # Development tools
    GIT = "git"
    DOCKER = "docker"
    KUBERNETES = "kubernetes"

    # Languages
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    RUST = "rust"
    GO = "go"

    # AI/ML
    GPU = "gpu"
    ML_FRAMEWORKS = "ml_frameworks"

    # Network
    INTERNET = "internet"
    VPN = "vpn"
    SSH = "ssh"

    # Security
    SECRETS_ACCESS = "secrets_access"
    ADMIN = "admin"


class ComputerStatus(str, Enum):
    """Status of a computer in the registry."""

    ONLINE = "online"
    OFFLINE = "offline"
    BUSY = "busy"
    MAINTENANCE = "maintenance"
    ERROR = "error"


@dataclass
class ComputerHealth:
    """Health metrics for a computer."""

    # CPU usage (0-100)
    cpu_percent: float = 0.0

    # Memory usage (0-100)
    memory_percent: float = 0.0

    # Disk usage (0-100)
    disk_percent: float = 0.0

    # Number of active tasks
    active_tasks: int = 0

    # Response latency in ms
    latency_ms: float = 0.0

    # Last health check
    last_check: datetime = field(default_factory=datetime.utcnow)

    # Error count in last hour
    error_count: int = 0

    def is_healthy(self) -> bool:
        """Check if computer is healthy."""
        return (
            self.cpu_percent < 90
            and self.memory_percent < 90
            and self.disk_percent < 95
            and self.error_count < 10
            and self.latency_ms < 5000
        )


@dataclass
class ComputerMetrics:
    """Performance metrics for a computer."""

    # Total tasks completed
    tasks_completed: int = 0

    # Total tasks failed
    tasks_failed: int = 0

    # Average task duration in seconds
    avg_task_duration: float = 0.0

    # Success rate (0-1)
    success_rate: float = 1.0

    # Total uptime in seconds
    uptime_seconds: float = 0.0

    # When metrics were last updated
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Computer:
    """A computer in the network."""

    # Unique identifier
    id: str

    # Human-readable name
    name: str

    # Capabilities this computer has
    capabilities: list[ComputerCapability] = field(default_factory=list)

    # Current status
    status: ComputerStatus = ComputerStatus.OFFLINE

    # Health metrics
    health: ComputerHealth = field(default_factory=ComputerHealth)

    # Performance metrics
    metrics: ComputerMetrics = field(default_factory=ComputerMetrics)

    # Host address (IP or hostname)
    host: str | None = None

    # Port for communication
    port: int | None = None

    # API key for authentication
    api_key: str | None = None

    # Tags for grouping
    tags: list[str] = field(default_factory=list)

    # Custom metadata
    metadata: dict[str, Any] = field(default_factory=dict)

    # When computer was registered
    registered_at: datetime = field(default_factory=datetime.utcnow)

    # When computer was last seen
    last_seen: datetime = field(default_factory=datetime.utcnow)

    # Maximum concurrent tasks
    max_concurrent_tasks: int = 5

    # Current task count
    current_tasks: int = 0

    def has_capability(self, capability: ComputerCapability) -> bool:
        """Check if computer has a specific capability."""
        return capability in self.capabilities

    def has_all_capabilities(self, capabilities: list[ComputerCapability]) -> bool:
        """Check if computer has all specified capabilities."""
        return all(c in self.capabilities for c in capabilities)

    def has_any_capability(self, capabilities: list[ComputerCapability]) -> bool:
        """Check if computer has any of the specified capabilities."""
        return any(c in self.capabilities for c in capabilities)

    def can_accept_task(self) -> bool:
        """Check if computer can accept a new task."""
        return (
            self.status == ComputerStatus.ONLINE
            and self.health.is_healthy()
            and self.current_tasks < self.max_concurrent_tasks
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "capabilities": [c.value for c in self.capabilities],
            "status": self.status.value,
            "host": self.host,
            "port": self.port,
            "tags": self.tags,
            "metadata": self.metadata,
            "registered_at": self.registered_at.isoformat(),
            "last_seen": self.last_seen.isoformat(),
            "max_concurrent_tasks": self.max_concurrent_tasks,
            "current_tasks": self.current_tasks,
            "health": {
                "cpu_percent": self.health.cpu_percent,
                "memory_percent": self.health.memory_percent,
                "disk_percent": self.health.disk_percent,
                "active_tasks": self.health.active_tasks,
                "latency_ms": self.health.latency_ms,
                "error_count": self.health.error_count,
            },
            "metrics": {
                "tasks_completed": self.metrics.tasks_completed,
                "tasks_failed": self.metrics.tasks_failed,
                "avg_task_duration": self.metrics.avg_task_duration,
                "success_rate": self.metrics.success_rate,
            },
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Computer":
        """Create from dictionary."""
        computer = cls(
            id=data["id"],
            name=data["name"],
            capabilities=[ComputerCapability(c) for c in data.get("capabilities", [])],
            status=ComputerStatus(data.get("status", "offline")),
            host=data.get("host"),
            port=data.get("port"),
            tags=data.get("tags", []),
            metadata=data.get("metadata", {}),
            max_concurrent_tasks=data.get("max_concurrent_tasks", 5),
            current_tasks=data.get("current_tasks", 0),
        )

        if "registered_at" in data:
            computer.registered_at = datetime.fromisoformat(data["registered_at"])
        if "last_seen" in data:
            computer.last_seen = datetime.fromisoformat(data["last_seen"])

        if "health" in data:
            h = data["health"]
            computer.health = ComputerHealth(
                cpu_percent=h.get("cpu_percent", 0),
                memory_percent=h.get("memory_percent", 0),
                disk_percent=h.get("disk_percent", 0),
                active_tasks=h.get("active_tasks", 0),
                latency_ms=h.get("latency_ms", 0),
                error_count=h.get("error_count", 0),
            )

        if "metrics" in data:
            m = data["metrics"]
            computer.metrics = ComputerMetrics(
                tasks_completed=m.get("tasks_completed", 0),
                tasks_failed=m.get("tasks_failed", 0),
                avg_task_duration=m.get("avg_task_duration", 0),
                success_rate=m.get("success_rate", 1.0),
            )

        return computer
