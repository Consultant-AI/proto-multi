"""
Proto Thinking Module - Extended thinking budget management.

Provides automatic detection and management of thinking budgets
for complex reasoning tasks.

Usage:
    from computer_use_demo.thinking import (
        ThinkingBudget,
        auto_detect_budget,
        get_api_thinking_config,
    )

    # Auto-detect from prompt
    result = auto_detect_budget("Design a scalable microservices architecture")
    print(f"Recommended: {result.budget} tokens ({result.reason})")

    # Get API config
    config = get_api_thinking_config(result.budget)
    # Pass to Anthropic API as extra_body

Budget Levels:
    - NONE (0): No extended thinking
    - THINK (4000): Basic thinking for standard tasks
    - MEGATHINK (10000): Extended thinking for complex analysis
    - ULTRATHINK (31999): Maximum thinking for architecture/planning

Auto-Detection:
    The detector analyzes prompts for keywords indicating complexity:
    - Architecture, design, planning → ULTRATHINK
    - Debug, analyze, optimize → MEGATHINK
    - Implement, add, create → THINK
    - Fix typo, rename → NONE

Override:
    Users can override detection by including keywords:
    - "[ultrathink]" or "ultrathink:" in prompt
    - "think harder" or "think deeply"
"""

from .budget import (
    ThinkingBudget,
    THINK,
    MEGATHINK,
    ULTRATHINK,
    clamp_budget,
    get_api_thinking_config,
    get_budget_name,
    parse_budget,
    should_use_thinking,
)

from .detector import (
    DetectionResult,
    ThinkingDetector,
    auto_detect_budget,
    get_thinking_detector,
)

__all__ = [
    # Budget
    "ThinkingBudget",
    "THINK",
    "MEGATHINK",
    "ULTRATHINK",
    "clamp_budget",
    "get_api_thinking_config",
    "get_budget_name",
    "parse_budget",
    "should_use_thinking",
    # Detector
    "DetectionResult",
    "ThinkingDetector",
    "auto_detect_budget",
    "get_thinking_detector",
]
