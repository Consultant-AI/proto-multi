"""
Health monitoring for system components.

Tracks health status, sends heartbeats, and detects failures.
"""

import asyncio
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable


class HealthStatus(str, Enum):
    """Health status of a component."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class HealthCheck:
    """Result of a health check."""

    status: HealthStatus
    message: str = ""
    latency_ms: float = 0.0
    details: dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)


@dataclass
class ComponentHealth:
    """Health tracking for a single component."""

    name: str
    status: HealthStatus = HealthStatus.UNKNOWN
    last_heartbeat: float | None = None
    last_check: HealthCheck | None = None
    consecutive_failures: int = 0
    total_checks: int = 0
    failed_checks: int = 0

    @property
    def uptime_percentage(self) -> float:
        """Calculate uptime percentage."""
        if self.total_checks == 0:
            return 100.0
        return ((self.total_checks - self.failed_checks) / self.total_checks) * 100


class HealthMonitor:
    """
    Monitors health of system components.

    Features:
    - Heartbeat tracking
    - Health check execution
    - Status aggregation
    - Alert callbacks
    """

    def __init__(
        self,
        heartbeat_interval: float = 30.0,
        heartbeat_timeout: float = 90.0,
        check_interval: float = 60.0,
    ):
        """
        Initialize health monitor.

        Args:
            heartbeat_interval: Expected interval between heartbeats (seconds)
            heartbeat_timeout: Time without heartbeat before marking unhealthy
            check_interval: Interval between health checks (seconds)
        """
        self._heartbeat_interval = heartbeat_interval
        self._heartbeat_timeout = heartbeat_timeout
        self._check_interval = check_interval

        self._components: dict[str, ComponentHealth] = {}
        self._health_checks: dict[str, Callable[[], HealthCheck]] = {}
        self._alert_callbacks: list[Callable[[str, HealthStatus, str], None]] = []

        self._running = False
        self._monitor_task: asyncio.Task | None = None

    def register_component(
        self,
        name: str,
        health_check: Callable[[], HealthCheck] | None = None,
    ) -> None:
        """
        Register a component to monitor.

        Args:
            name: Unique component name
            health_check: Optional function to check health
        """
        self._components[name] = ComponentHealth(name=name)
        if health_check:
            self._health_checks[name] = health_check

    def unregister_component(self, name: str) -> None:
        """Unregister a component."""
        self._components.pop(name, None)
        self._health_checks.pop(name, None)

    def add_alert_callback(
        self,
        callback: Callable[[str, HealthStatus, str], None],
    ) -> None:
        """
        Add callback for health alerts.

        Callback receives (component_name, new_status, message).
        """
        self._alert_callbacks.append(callback)

    def heartbeat(self, component_name: str) -> None:
        """
        Record a heartbeat from a component.

        Args:
            component_name: Name of the component sending heartbeat
        """
        if component_name not in self._components:
            self.register_component(component_name)

        component = self._components[component_name]
        component.last_heartbeat = time.time()

        # If was unhealthy due to missing heartbeats, mark healthy
        if component.status == HealthStatus.UNHEALTHY:
            component.consecutive_failures = 0
            self._update_status(component_name, HealthStatus.HEALTHY, "Heartbeat received")

    def report_health(self, component_name: str, check: HealthCheck) -> None:
        """
        Report health check result for a component.

        Args:
            component_name: Name of the component
            check: Health check result
        """
        if component_name not in self._components:
            self.register_component(component_name)

        component = self._components[component_name]
        component.last_check = check
        component.total_checks += 1

        if check.status != HealthStatus.HEALTHY:
            component.consecutive_failures += 1
            component.failed_checks += 1
        else:
            component.consecutive_failures = 0

        self._update_status(component_name, check.status, check.message)

    def get_health(self, component_name: str) -> ComponentHealth | None:
        """Get health info for a component."""
        return self._components.get(component_name)

    def get_all_health(self) -> dict[str, ComponentHealth]:
        """Get health info for all components."""
        return self._components.copy()

    def get_overall_status(self) -> HealthStatus:
        """
        Get overall system health status.

        Returns UNHEALTHY if any component is unhealthy,
        DEGRADED if any is degraded, HEALTHY otherwise.
        """
        if not self._components:
            return HealthStatus.UNKNOWN

        statuses = [c.status for c in self._components.values()]

        if HealthStatus.UNHEALTHY in statuses:
            return HealthStatus.UNHEALTHY
        if HealthStatus.DEGRADED in statuses:
            return HealthStatus.DEGRADED
        if HealthStatus.UNKNOWN in statuses:
            return HealthStatus.UNKNOWN

        return HealthStatus.HEALTHY

    def _update_status(
        self,
        component_name: str,
        new_status: HealthStatus,
        message: str = "",
    ) -> None:
        """Update component status and fire alerts if changed."""
        component = self._components.get(component_name)
        if not component:
            return

        old_status = component.status
        component.status = new_status

        # Fire alert if status changed
        if old_status != new_status:
            for callback in self._alert_callbacks:
                try:
                    callback(component_name, new_status, message)
                except Exception as e:
                    print(f"[Health] Alert callback error: {e}")

    async def _check_heartbeats(self) -> None:
        """Check for missing heartbeats."""
        now = time.time()
        timeout = self._heartbeat_timeout

        for name, component in self._components.items():
            if component.last_heartbeat:
                elapsed = now - component.last_heartbeat
                if elapsed > timeout:
                    self._update_status(
                        name,
                        HealthStatus.UNHEALTHY,
                        f"No heartbeat for {elapsed:.1f}s (timeout: {timeout}s)",
                    )

    async def _run_health_checks(self) -> None:
        """Run registered health checks."""
        for name, check_func in self._health_checks.items():
            try:
                start = time.time()
                check = check_func()
                check.latency_ms = (time.time() - start) * 1000
                self.report_health(name, check)
            except Exception as e:
                self.report_health(
                    name,
                    HealthCheck(
                        status=HealthStatus.UNHEALTHY,
                        message=f"Health check failed: {e}",
                    ),
                )

    async def _monitor_loop(self) -> None:
        """Main monitoring loop."""
        while self._running:
            await self._check_heartbeats()
            await self._run_health_checks()
            await asyncio.sleep(self._check_interval)

    async def start(self) -> None:
        """Start the health monitor."""
        if self._running:
            return

        self._running = True
        self._monitor_task = asyncio.create_task(self._monitor_loop())
        print("[Health] Monitor started")

    async def stop(self) -> None:
        """Stop the health monitor."""
        self._running = False
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
            self._monitor_task = None
        print("[Health] Monitor stopped")


# Global health monitor instance
_health_monitor: HealthMonitor | None = None


def get_health_monitor() -> HealthMonitor:
    """Get the global health monitor instance."""
    global _health_monitor
    if _health_monitor is None:
        _health_monitor = HealthMonitor()
    return _health_monitor


def heartbeat(component_name: str) -> None:
    """Convenience function to send heartbeat to global monitor."""
    get_health_monitor().heartbeat(component_name)
