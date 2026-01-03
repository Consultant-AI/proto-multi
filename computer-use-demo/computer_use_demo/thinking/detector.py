"""
Auto-detection of thinking budget based on task complexity.

Analyzes user prompts to determine appropriate thinking budget.
"""

import re
from dataclasses import dataclass
from typing import Any

from .budget import ThinkingBudget, parse_budget


@dataclass
class DetectionResult:
    """Result of thinking budget detection."""

    # Recommended budget
    budget: int

    # Reason for the recommendation
    reason: str

    # Confidence (0-1)
    confidence: float

    # Keywords found
    keywords_found: list[str]

    # Was override detected?
    override_detected: bool


class ThinkingDetector:
    """
    Detects appropriate thinking budget based on task complexity.

    Uses keyword matching and heuristics to determine budget.
    """

    def __init__(self):
        # Keywords that suggest ultrathink (architecture, planning)
        self._ultrathink_keywords = [
            # Architecture keywords
            r"\barchitect\w*\b",
            r"\bdesign\s+system\b",
            r"\bsystem\s+design\b",
            r"\bscalable\b",
            r"\bdistributed\b",
            r"\bmicroservice\w*\b",
            # Planning keywords
            r"\bplan\s+(the|a|this)\b",
            r"\bstrateg\w+\b",
            r"\broadmap\b",
            r"\bimplementation\s+plan\b",
            # Complex analysis
            r"\banalyze\s+(the\s+)?architecture\b",
            r"\brefactor\s+(the\s+)?(entire|whole|complete)\b",
            r"\bmigrat\w+\b",
            r"\bre-?architect\b",
            # Explicit request
            r"\bultrathink\b",
            r"\bthink\s+(very\s+)?hard\b",
            r"\bthink\s+deeply\b",
        ]

        # Keywords that suggest megathink (debugging, complex analysis)
        self._megathink_keywords = [
            # Debugging
            r"\bdebug\w*\b",
            r"\btroubleshoot\w*\b",
            r"\broot\s+cause\b",
            r"\brace\s+condition\b",
            r"\bdeadlock\b",
            r"\bmemory\s+leak\b",
            # Complex analysis
            r"\banalyz\w+\b",
            r"\bcomplex\b",
            r"\boptimiz\w+\b",
            r"\bperformance\b",
            r"\bbottleneck\b",
            r"\bsecurity\s+(audit|review)\b",
            # Code review
            r"\breview\s+(the\s+)?code\b",
            r"\bcode\s+review\b",
            # Explicit request
            r"\bmegathink\b",
            r"\bthink\s+harder\b",
        ]

        # Keywords that suggest think (standard coding)
        self._think_keywords = [
            r"\badd\s+(a\s+)?feature\b",
            r"\bimplement\b",
            r"\bcreate\s+(a\s+)?new\b",
            r"\bbuild\s+(a\s+)?\b",
            r"\bwrite\s+(a\s+)?(function|class|method)\b",
            r"\brefactor\s+(this|the)\b",
            r"\bupdate\b",
            r"\bmodify\b",
            # Explicit request
            r"\bthink\b",
        ]

        # Keywords that suggest no thinking (simple tasks)
        self._none_keywords = [
            r"\bfix\s+(the\s+)?typo\b",
            r"\brename\b",
            r"\bsimple\b",
            r"\bquick\b",
            r"\bjust\s+(add|change|update)\b",
            r"\bminor\b",
        ]

    def detect(
        self,
        prompt: str,
        context: dict[str, Any] | None = None,
        default_budget: int | None = None,
    ) -> DetectionResult:
        """
        Detect appropriate thinking budget for a prompt.

        Args:
            prompt: User's prompt/message
            context: Optional context (previous messages, etc.)
            default_budget: Default budget if no detection

        Returns:
            DetectionResult with recommended budget
        """
        prompt_lower = prompt.lower()
        keywords_found = []

        # Check for explicit override first
        override = self._check_override(prompt_lower)
        if override is not None:
            return DetectionResult(
                budget=override,
                reason="Explicit override in prompt",
                confidence=1.0,
                keywords_found=[],
                override_detected=True,
            )

        # Check ultrathink keywords
        ultra_matches = self._match_keywords(prompt_lower, self._ultrathink_keywords)
        if ultra_matches:
            return DetectionResult(
                budget=ThinkingBudget.ULTRATHINK,
                reason="Complex architecture/planning task",
                confidence=0.9,
                keywords_found=ultra_matches,
                override_detected=False,
            )

        # Check megathink keywords
        mega_matches = self._match_keywords(prompt_lower, self._megathink_keywords)
        if mega_matches:
            return DetectionResult(
                budget=ThinkingBudget.MEGATHINK,
                reason="Complex analysis/debugging task",
                confidence=0.8,
                keywords_found=mega_matches,
                override_detected=False,
            )

        # Check think keywords
        think_matches = self._match_keywords(prompt_lower, self._think_keywords)
        if think_matches:
            return DetectionResult(
                budget=ThinkingBudget.THINK,
                reason="Standard coding task",
                confidence=0.7,
                keywords_found=think_matches,
                override_detected=False,
            )

        # Check none keywords
        none_matches = self._match_keywords(prompt_lower, self._none_keywords)
        if none_matches:
            return DetectionResult(
                budget=ThinkingBudget.NONE,
                reason="Simple task",
                confidence=0.8,
                keywords_found=none_matches,
                override_detected=False,
            )

        # Default based on prompt length and complexity heuristics
        budget = self._estimate_from_heuristics(prompt, context)

        return DetectionResult(
            budget=budget if budget is not None else (default_budget or ThinkingBudget.NONE),
            reason="Heuristic estimation",
            confidence=0.5,
            keywords_found=[],
            override_detected=False,
        )

    def _check_override(self, prompt: str) -> int | None:
        """Check for explicit thinking budget override in prompt."""
        # Look for patterns like "ultrathink:", "[ultrathink]", etc.
        override_patterns = [
            (r"\[ultrathink\]", ThinkingBudget.ULTRATHINK),
            (r"\[megathink\]", ThinkingBudget.MEGATHINK),
            (r"\[think\]", ThinkingBudget.THINK),
            (r"ultrathink:", ThinkingBudget.ULTRATHINK),
            (r"megathink:", ThinkingBudget.MEGATHINK),
            (r"think:", ThinkingBudget.THINK),
        ]

        for pattern, budget in override_patterns:
            if re.search(pattern, prompt, re.IGNORECASE):
                return budget

        return None

    def _match_keywords(self, text: str, patterns: list[str]) -> list[str]:
        """Find all matching keywords in text."""
        matches = []
        for pattern in patterns:
            found = re.findall(pattern, text, re.IGNORECASE)
            matches.extend(found)
        return matches

    def _estimate_from_heuristics(
        self,
        prompt: str,
        context: dict[str, Any] | None,
    ) -> int | None:
        """Estimate budget from heuristics when keywords don't match."""
        # Long prompts might need more thinking
        if len(prompt) > 2000:
            return ThinkingBudget.MEGATHINK
        if len(prompt) > 500:
            return ThinkingBudget.THINK

        # Check if it looks like a multi-step task
        step_indicators = [
            r"\bfirst\b.*\bthen\b",
            r"\b1\.\s",
            r"\bstep\s*\d",
            r"\bafter\s+that\b",
        ]
        for pattern in step_indicators:
            if re.search(pattern, prompt, re.IGNORECASE):
                return ThinkingBudget.THINK

        # Default to no thinking for short, simple prompts
        return None


# Global detector instance
_detector: ThinkingDetector | None = None


def get_thinking_detector() -> ThinkingDetector:
    """Get the global thinking detector instance."""
    global _detector
    if _detector is None:
        _detector = ThinkingDetector()
    return _detector


def auto_detect_budget(
    prompt: str,
    context: dict[str, Any] | None = None,
    default_budget: int | None = None,
) -> DetectionResult:
    """
    Convenience function for auto-detecting thinking budget.

    Args:
        prompt: User's prompt
        context: Optional context
        default_budget: Default if no detection

    Returns:
        DetectionResult
    """
    return get_thinking_detector().detect(prompt, context, default_budget)
