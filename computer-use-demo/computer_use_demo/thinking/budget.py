"""
Thinking budget management for extended thinking.

Defines thinking budget levels and provides utilities for managing them.
"""

from enum import IntEnum
from typing import Any


class ThinkingBudget(IntEnum):
    """
    Thinking budget levels in tokens.

    Higher budgets allow more complex reasoning but cost more.
    """

    # No extended thinking
    NONE = 0

    # Basic thinking for standard tasks
    THINK = 4000

    # Extended thinking for complex analysis
    MEGATHINK = 10000

    # Maximum thinking for architecture and hard problems
    ULTRATHINK = 31999


# Aliases for convenience
THINK = ThinkingBudget.THINK
MEGATHINK = ThinkingBudget.MEGATHINK
ULTRATHINK = ThinkingBudget.ULTRATHINK


def get_budget_name(budget: int | ThinkingBudget) -> str:
    """Get human-readable name for a thinking budget."""
    if budget == 0:
        return "none"
    elif budget <= 4000:
        return "think"
    elif budget <= 10000:
        return "megathink"
    else:
        return "ultrathink"


def parse_budget(value: str | int | None) -> int | None:
    """
    Parse a thinking budget from various formats.

    Args:
        value: Can be:
            - None: Return None (no explicit budget)
            - int: Return as-is
            - str: Parse as keyword or number

    Returns:
        Budget in tokens, or None for no explicit budget
    """
    if value is None:
        return None

    if isinstance(value, int):
        return value

    if isinstance(value, str):
        value_lower = value.lower().strip()

        # Check keywords
        keywords = {
            "none": ThinkingBudget.NONE,
            "think": ThinkingBudget.THINK,
            "megathink": ThinkingBudget.MEGATHINK,
            "ultrathink": ThinkingBudget.ULTRATHINK,
            "ultra": ThinkingBudget.ULTRATHINK,
            "max": ThinkingBudget.ULTRATHINK,
        }

        if value_lower in keywords:
            return keywords[value_lower]

        # Try parsing as number
        try:
            return int(value)
        except ValueError:
            pass

    return None


def clamp_budget(budget: int, min_budget: int = 0, max_budget: int = 31999) -> int:
    """Clamp budget to valid range."""
    return max(min_budget, min(budget, max_budget))


def should_use_thinking(budget: int | None) -> bool:
    """Check if extended thinking should be used."""
    return budget is not None and budget > 0


def get_api_thinking_config(budget: int | None) -> dict[str, Any] | None:
    """
    Get the API configuration for extended thinking.

    Returns dict for extra_body parameter, or None if no thinking.
    """
    if not should_use_thinking(budget):
        return None

    return {
        "thinking": {
            "type": "enabled",
            "budget_tokens": clamp_budget(budget),
        }
    }
