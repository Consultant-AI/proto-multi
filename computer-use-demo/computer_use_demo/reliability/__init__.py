"""
Proto Reliability Module - Fault tolerance and resilience patterns.

This module provides production-grade reliability mechanisms:
- Circuit breakers to prevent cascading failures
- Retry logic with exponential backoff
- Checkpointing for recovery
- Health monitoring
- Idempotency for safe retries

Usage:
    from computer_use_demo.reliability import (
        # Circuit breakers
        CircuitBreaker,
        get_circuit_breaker,

        # Retry
        with_retry,
        retry_async,
        RetryConfig,

        # Checkpoints
        get_checkpoint_manager,

        # Health
        get_health_monitor,
        heartbeat,

        # Idempotency
        get_idempotency_manager,
    )

    # Use circuit breaker
    breaker = get_circuit_breaker("anthropic_api")

    @breaker
    async def call_api():
        ...

    # Use retry
    @with_retry(RetryConfig(max_attempts=3))
    async def fetch_data():
        ...

    # Send heartbeats
    heartbeat("my_component")
"""

from .circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerConfig,
    CircuitBreakerStats,
    CircuitOpenError,
    CircuitState,
    get_all_circuit_breakers,
    get_circuit_breaker,
    reset_all_circuit_breakers,
)

from .retry import (
    RetryConfig,
    RetryStats,
    calculate_delay,
    retry_async,
    retry_sync,
    should_retry,
    with_retry,
    RETRY_API_CONFIG,
    RETRY_NETWORK_CONFIG,
    RETRY_AGGRESSIVE_CONFIG,
)

from .checkpoint import (
    Checkpoint,
    CheckpointManager,
    get_checkpoint_manager,
)

from .health import (
    ComponentHealth,
    HealthCheck,
    HealthMonitor,
    HealthStatus,
    get_health_monitor,
    heartbeat,
)

from .idempotency import (
    IdempotencyManager,
    IdempotencyRecord,
    get_idempotency_manager,
)

__all__ = [
    # Circuit Breaker
    "CircuitBreaker",
    "CircuitBreakerConfig",
    "CircuitBreakerStats",
    "CircuitOpenError",
    "CircuitState",
    "get_circuit_breaker",
    "get_all_circuit_breakers",
    "reset_all_circuit_breakers",
    # Retry
    "RetryConfig",
    "RetryStats",
    "calculate_delay",
    "retry_async",
    "retry_sync",
    "should_retry",
    "with_retry",
    "RETRY_API_CONFIG",
    "RETRY_NETWORK_CONFIG",
    "RETRY_AGGRESSIVE_CONFIG",
    # Checkpoint
    "Checkpoint",
    "CheckpointManager",
    "get_checkpoint_manager",
    # Health
    "ComponentHealth",
    "HealthCheck",
    "HealthMonitor",
    "HealthStatus",
    "get_health_monitor",
    "heartbeat",
    # Idempotency
    "IdempotencyManager",
    "IdempotencyRecord",
    "get_idempotency_manager",
]
