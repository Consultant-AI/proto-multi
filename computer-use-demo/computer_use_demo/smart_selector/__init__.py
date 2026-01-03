"""
Smart Model & Thinking Selection System.

Uses a lightweight Haiku classifier to intelligently select:
1. Which model to use (Haiku vs Sonnet vs Opus)
2. How much thinking budget to allocate (0 → 31,999 tokens)

Philosophy: Act like Opus is always on. Only use weaker models
when the result would be IDENTICAL (zero quality difference).
"""

from .models import SelectionResult, ModelConfig, TaskType, Phase
from .selector import SmartSelector
from .escalation import AdaptiveExecutor

__all__ = [
    "SmartSelector",
    "SelectionResult",
    "ModelConfig",
    "TaskType",
    "Phase",
    "AdaptiveExecutor",
]
