"""
Retry logic with exponential backoff and jitter.

Provides robust retry mechanisms for transient failures.
"""

import asyncio
import random
import time
from dataclasses import dataclass
from functools import wraps
from typing import Any, Callable, Sequence, Type, TypeVar

T = TypeVar("T")


@dataclass
class RetryConfig:
    """Configuration for retry behavior."""

    # Maximum number of retry attempts
    max_attempts: int = 5

    # Initial delay between retries (seconds)
    initial_delay: float = 1.0

    # Maximum delay between retries (seconds)
    max_delay: float = 60.0

    # Multiplier for exponential backoff
    backoff_multiplier: float = 2.0

    # Random jitter factor (0 to 1)
    jitter: float = 0.25

    # Exception types to retry on (empty = retry all)
    retryable_exceptions: tuple[Type[Exception], ...] = ()

    # Exception types to NOT retry on
    non_retryable_exceptions: tuple[Type[Exception], ...] = ()

    # HTTP status codes to retry on (for HTTP errors)
    retryable_status_codes: tuple[int, ...] = (429, 500, 502, 503, 504)

    # HTTP status codes to NOT retry on
    non_retryable_status_codes: tuple[int, ...] = (400, 401, 403, 404)


@dataclass
class RetryStats:
    """Statistics from a retry operation."""

    attempts: int = 0
    total_delay: float = 0.0
    success: bool = False
    last_error: Exception | None = None


def calculate_delay(
    attempt: int,
    config: RetryConfig,
) -> float:
    """
    Calculate delay for next retry using exponential backoff with jitter.

    Formula: min(max_delay, initial_delay * (backoff_multiplier ^ attempt) * (1 + random_jitter))
    """
    # Calculate base delay with exponential backoff
    delay = config.initial_delay * (config.backoff_multiplier ** attempt)

    # Apply jitter
    jitter_range = delay * config.jitter
    delay = delay + random.uniform(-jitter_range, jitter_range)

    # Clamp to max delay
    return min(delay, config.max_delay)


def should_retry(
    error: Exception,
    config: RetryConfig,
) -> bool:
    """
    Determine if an exception should trigger a retry.

    Returns True if the error is retryable according to config.
    """
    # Check non-retryable exceptions first
    if config.non_retryable_exceptions:
        if isinstance(error, config.non_retryable_exceptions):
            return False

    # Check retryable exceptions
    if config.retryable_exceptions:
        if not isinstance(error, config.retryable_exceptions):
            return False

    # Check HTTP status codes if error has one
    status_code = getattr(error, "status_code", None) or getattr(error, "status", None)
    if status_code:
        if config.non_retryable_status_codes and status_code in config.non_retryable_status_codes:
            return False
        if config.retryable_status_codes and status_code not in config.retryable_status_codes:
            return False

    return True


async def retry_async(
    func: Callable[..., Any],
    *args,
    config: RetryConfig | None = None,
    on_retry: Callable[[int, Exception, float], None] | None = None,
    **kwargs,
) -> tuple[Any, RetryStats]:
    """
    Execute an async function with retry logic.

    Args:
        func: Async function to execute
        *args: Positional arguments for func
        config: Retry configuration
        on_retry: Optional callback(attempt, error, delay) called before each retry
        **kwargs: Keyword arguments for func

    Returns:
        Tuple of (result, stats)

    Raises:
        The last exception if all retries fail
    """
    config = config or RetryConfig()
    stats = RetryStats()

    last_error: Exception | None = None

    for attempt in range(config.max_attempts):
        stats.attempts = attempt + 1

        try:
            result = await func(*args, **kwargs)
            stats.success = True
            return result, stats

        except Exception as e:
            last_error = e
            stats.last_error = e

            # Check if we should retry
            if not should_retry(e, config):
                raise

            # Check if we have more attempts
            if attempt + 1 >= config.max_attempts:
                raise

            # Calculate delay
            delay = calculate_delay(attempt, config)
            stats.total_delay += delay

            # Notify retry callback
            if on_retry:
                on_retry(attempt + 1, e, delay)

            # Wait before retry
            await asyncio.sleep(delay)

    # Should never reach here, but just in case
    if last_error:
        raise last_error
    raise RuntimeError("Retry exhausted without result or error")


def with_retry(
    config: RetryConfig | None = None,
    on_retry: Callable[[int, Exception, float], None] | None = None,
) -> Callable:
    """
    Decorator for adding retry logic to async functions.

    Usage:
        @with_retry(RetryConfig(max_attempts=3))
        async def fetch_data():
            ...

        # Or with default config
        @with_retry()
        async def fetch_data():
            ...
    """
    _config = config or RetryConfig()

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            result, _ = await retry_async(
                func, *args, config=_config, on_retry=on_retry, **kwargs
            )
            return result

        return wrapper

    return decorator


def retry_sync(
    func: Callable[..., T],
    *args,
    config: RetryConfig | None = None,
    on_retry: Callable[[int, Exception, float], None] | None = None,
    **kwargs,
) -> tuple[T, RetryStats]:
    """
    Execute a synchronous function with retry logic.

    Same as retry_async but for sync functions.
    """
    config = config or RetryConfig()
    stats = RetryStats()

    last_error: Exception | None = None

    for attempt in range(config.max_attempts):
        stats.attempts = attempt + 1

        try:
            result = func(*args, **kwargs)
            stats.success = True
            return result, stats

        except Exception as e:
            last_error = e
            stats.last_error = e

            # Check if we should retry
            if not should_retry(e, config):
                raise

            # Check if we have more attempts
            if attempt + 1 >= config.max_attempts:
                raise

            # Calculate delay
            delay = calculate_delay(attempt, config)
            stats.total_delay += delay

            # Notify retry callback
            if on_retry:
                on_retry(attempt + 1, e, delay)

            # Wait before retry
            time.sleep(delay)

    # Should never reach here, but just in case
    if last_error:
        raise last_error
    raise RuntimeError("Retry exhausted without result or error")


# Pre-configured retry configs for common use cases
RETRY_API_CONFIG = RetryConfig(
    max_attempts=5,
    initial_delay=1.0,
    max_delay=30.0,
    backoff_multiplier=2.0,
    jitter=0.25,
    retryable_status_codes=(429, 500, 502, 503, 504),
    non_retryable_status_codes=(400, 401, 403, 404),
)

RETRY_NETWORK_CONFIG = RetryConfig(
    max_attempts=3,
    initial_delay=0.5,
    max_delay=10.0,
    backoff_multiplier=2.0,
    jitter=0.1,
)

RETRY_AGGRESSIVE_CONFIG = RetryConfig(
    max_attempts=10,
    initial_delay=0.1,
    max_delay=60.0,
    backoff_multiplier=1.5,
    jitter=0.3,
)
