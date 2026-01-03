"""
Circuit Breaker pattern implementation.

Prevents cascading failures by temporarily blocking requests to failing services.
States: CLOSED (normal) -> OPEN (failing) -> HALF_OPEN (testing recovery)
"""

import asyncio
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, TypeVar

T = TypeVar("T")


class CircuitState(str, Enum):
    """Circuit breaker states."""

    CLOSED = "closed"      # Normal operation, requests flow through
    OPEN = "open"          # Failing, requests immediately rejected
    HALF_OPEN = "half_open"  # Testing if service recovered


@dataclass
class CircuitBreakerConfig:
    """Configuration for a circuit breaker."""

    # Number of failures before opening the circuit
    failure_threshold: int = 5

    # Time window for counting failures (seconds)
    failure_window: float = 60.0

    # How long to wait before testing recovery (seconds)
    recovery_timeout: float = 30.0

    # Number of successful requests in half-open before closing
    success_threshold: int = 1

    # Optional name for logging
    name: str = "default"


@dataclass
class CircuitBreakerStats:
    """Statistics for circuit breaker monitoring."""

    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    rejected_requests: int = 0
    state_changes: int = 0
    last_failure_time: float | None = None
    last_success_time: float | None = None
    current_state: CircuitState = CircuitState.CLOSED


class CircuitBreaker:
    """
    Circuit breaker for preventing cascading failures.

    Usage:
        breaker = CircuitBreaker(name="anthropic_api")

        # With decorator
        @breaker
        async def call_api():
            return await client.messages.create(...)

        # Or manually
        async with breaker:
            result = await client.messages.create(...)

        # Or check state
        if breaker.is_available():
            try:
                breaker.record_success()
            except Exception:
                breaker.record_failure()
    """

    def __init__(self, config: CircuitBreakerConfig | None = None, **kwargs):
        self._config = config or CircuitBreakerConfig(**kwargs)
        self._state = CircuitState.CLOSED
        self._failures: list[float] = []  # Timestamps of recent failures
        self._successes_in_half_open = 0
        self._opened_at: float | None = None
        self._stats = CircuitBreakerStats()
        self._lock = asyncio.Lock()

    @property
    def state(self) -> CircuitState:
        """Get current circuit state."""
        return self._state

    @property
    def stats(self) -> CircuitBreakerStats:
        """Get circuit breaker statistics."""
        self._stats.current_state = self._state
        return self._stats

    @property
    def name(self) -> str:
        """Get circuit breaker name."""
        return self._config.name

    def is_available(self) -> bool:
        """
        Check if requests can be made through this circuit.

        Returns True if circuit is CLOSED or HALF_OPEN.
        """
        self._check_recovery()
        return self._state != CircuitState.OPEN

    def _check_recovery(self) -> None:
        """Check if circuit should transition from OPEN to HALF_OPEN."""
        if self._state == CircuitState.OPEN and self._opened_at:
            elapsed = time.time() - self._opened_at
            if elapsed >= self._config.recovery_timeout:
                self._transition_to(CircuitState.HALF_OPEN)

    def _transition_to(self, new_state: CircuitState) -> None:
        """Transition to a new state."""
        if self._state != new_state:
            old_state = self._state
            self._state = new_state
            self._stats.state_changes += 1

            if new_state == CircuitState.OPEN:
                self._opened_at = time.time()
            elif new_state == CircuitState.HALF_OPEN:
                self._successes_in_half_open = 0
            elif new_state == CircuitState.CLOSED:
                self._failures.clear()

            print(f"[CircuitBreaker:{self.name}] {old_state.value} -> {new_state.value}")

    def record_success(self) -> None:
        """Record a successful request."""
        self._stats.total_requests += 1
        self._stats.successful_requests += 1
        self._stats.last_success_time = time.time()

        if self._state == CircuitState.HALF_OPEN:
            self._successes_in_half_open += 1
            if self._successes_in_half_open >= self._config.success_threshold:
                self._transition_to(CircuitState.CLOSED)

    def record_failure(self, error: Exception | None = None) -> None:
        """Record a failed request."""
        now = time.time()
        self._stats.total_requests += 1
        self._stats.failed_requests += 1
        self._stats.last_failure_time = now

        if self._state == CircuitState.HALF_OPEN:
            # Any failure in half-open goes back to open
            self._transition_to(CircuitState.OPEN)
            return

        if self._state == CircuitState.CLOSED:
            # Clean up old failures outside the window
            cutoff = now - self._config.failure_window
            self._failures = [t for t in self._failures if t > cutoff]

            # Add this failure
            self._failures.append(now)

            # Check if we should open the circuit
            if len(self._failures) >= self._config.failure_threshold:
                self._transition_to(CircuitState.OPEN)

    def record_rejection(self) -> None:
        """Record a rejected request (circuit open)."""
        self._stats.rejected_requests += 1

    def reset(self) -> None:
        """Reset circuit breaker to initial state."""
        self._state = CircuitState.CLOSED
        self._failures.clear()
        self._successes_in_half_open = 0
        self._opened_at = None

    async def __aenter__(self) -> "CircuitBreaker":
        """Context manager entry."""
        async with self._lock:
            if not self.is_available():
                self.record_rejection()
                raise CircuitOpenError(f"Circuit '{self.name}' is open")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> bool:
        """Context manager exit."""
        if exc_type is None:
            self.record_success()
        else:
            self.record_failure(exc_val)
        return False  # Don't suppress exceptions

    def __call__(self, func: Callable) -> Callable:
        """Decorator for wrapping async functions with circuit breaker."""

        async def wrapper(*args, **kwargs) -> Any:
            async with self:
                return await func(*args, **kwargs)

        return wrapper


class CircuitOpenError(Exception):
    """Raised when attempting to use an open circuit."""

    pass


# Global registry of circuit breakers
_circuit_breakers: dict[str, CircuitBreaker] = {}


def get_circuit_breaker(name: str, **kwargs) -> CircuitBreaker:
    """
    Get or create a circuit breaker by name.

    Args:
        name: Unique identifier for the circuit breaker
        **kwargs: Configuration options (only used if creating new)

    Returns:
        CircuitBreaker instance
    """
    if name not in _circuit_breakers:
        config = CircuitBreakerConfig(name=name, **kwargs)
        _circuit_breakers[name] = CircuitBreaker(config)
    return _circuit_breakers[name]


def get_all_circuit_breakers() -> dict[str, CircuitBreaker]:
    """Get all registered circuit breakers."""
    return _circuit_breakers.copy()


def reset_all_circuit_breakers() -> None:
    """Reset all circuit breakers to initial state."""
    for breaker in _circuit_breakers.values():
        breaker.reset()
