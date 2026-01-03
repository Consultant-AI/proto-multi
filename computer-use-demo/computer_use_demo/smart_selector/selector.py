"""
Smart Model & Thinking Selector.

Uses a lightweight Haiku classifier to intelligently select:
1. Which model to use (Haiku vs Sonnet vs Opus)
2. How much thinking budget to allocate (0 → 31,999 tokens)

Selection is PURELY CONTENT-BASED - analyzes actual task text.
No hardcoded rules based on phase, agent type, or labels.

Cost: ~$0.001 per classification (trivial overhead)
"""

import json
import re
from typing import Any

from anthropic import Anthropic

from .models import (
    HAIKU_4_5,
    MODELS,
    SONNET_4_5,
    TASK_TYPE_MODELS,
    TASK_TYPE_THINKING,
    Phase,
    SelectionResult,
    TaskType,
)
from .classifier_prompt import (
    FALLBACK_SELECTION,
    format_classifier_prompt,
)


class SmartSelector:
    """
    Uses Haiku to intelligently select model and thinking budget.

    Philosophy: Act like Opus is always on. Only use weaker models
    when the result would be IDENTICAL (zero quality difference).

    Selection is purely content-based - analyzes the actual task text,
    not labels like "phase" or "agent type".
    """

    def __init__(self, api_key: str | None = None):
        """Initialize the selector with Anthropic client."""
        self.client = Anthropic(api_key=api_key) if api_key else Anthropic()
        self.classifier_model = HAIKU_4_5.model_id

    async def select(
        self,
        task: str,
        context: dict | None = None,
    ) -> SelectionResult:
        """
        Analyze task and determine optimal model + thinking budget.

        Selection is purely content-based - analyzes the actual task text.

        Args:
            task: The task description
            context: Additional context (project info, etc.)

        Returns:
            SelectionResult with model, thinking budget, and reasoning
        """
        try:
            classification = await self._classify_task(
                task=task,
                context=context,
            )
            return self._build_result(classification)

        except Exception as e:
            # Fallback to safe defaults on error
            print(f"[SmartSelector] Classification failed: {e}, using fallback")
            return self._fallback_result()

    def select_sync(
        self,
        task: str,
        context: dict | None = None,
    ) -> SelectionResult:
        """
        Synchronous version of select().

        Selection is purely content-based - analyzes the actual task text.

        For use in non-async contexts.
        """
        try:
            classification = self._classify_task_sync(
                task=task,
                context=context,
            )
            return self._build_result(classification)

        except Exception as e:
            print(f"[SmartSelector] Classification failed: {e}, using fallback")
            return self._fallback_result()

    async def _classify_task(
        self,
        task: str,
        context: dict | None,
    ) -> dict:
        """Call Haiku classifier to analyze the task content."""
        prompt = format_classifier_prompt(
            task=task,
            context=context,
        )

        response = self.client.messages.create(
            model=self.classifier_model,
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}],
        )

        # Extract text response
        text = ""
        for block in response.content:
            if hasattr(block, "text"):
                text = block.text
                break

        return self._parse_classification(text)

    def _classify_task_sync(
        self,
        task: str,
        context: dict | None,
    ) -> dict:
        """Synchronous version of _classify_task."""
        prompt = format_classifier_prompt(
            task=task,
            context=context,
        )

        response = self.client.messages.create(
            model=self.classifier_model,
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}],
        )

        text = ""
        for block in response.content:
            if hasattr(block, "text"):
                text = block.text
                break

        return self._parse_classification(text)

    def _parse_classification(self, text: str) -> dict:
        """Parse JSON response from classifier."""
        try:
            # Try direct JSON parse
            return json.loads(text.strip())
        except json.JSONDecodeError:
            # Try to extract JSON from text
            json_match = re.search(r'\{[^{}]+\}', text, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except json.JSONDecodeError:
                    pass

        # Return fallback if parsing fails
        return FALLBACK_SELECTION.copy()

    def _build_result(self, classification: dict) -> SelectionResult:
        """Build SelectionResult from classification dict."""
        model = classification.get("model", "sonnet")
        if model not in MODELS:
            model = "sonnet"

        task_type_str = classification.get("task_type", "unknown")
        try:
            task_type = TaskType(task_type_str)
        except ValueError:
            task_type = TaskType.UNKNOWN

        thinking = classification.get("thinking_budget", 4000)
        # Validate thinking budget
        if thinking not in (0, 4000, 10000, 31999):
            thinking = 4000

        return SelectionResult(
            model=model,
            model_id=MODELS[model].model_id,
            thinking_budget=thinking,
            task_type=task_type,
            phase=Phase.UNKNOWN,  # Phase is just metadata now, not used for selection
            reasoning=classification.get("reasoning", "Classified by Haiku based on task content"),
            is_mechanical=classification.get("is_mechanical", False),
            quality_critical=classification.get("quality_critical", False),
            needs_tools=classification.get("needs_tools", True),
        )

    def _fallback_result(self) -> SelectionResult:
        """Return safe fallback selection."""
        # Ultimate fallback: Sonnet with moderate thinking
        return SelectionResult(
            model="sonnet",
            model_id=SONNET_4_5.model_id,
            thinking_budget=4000,
            task_type=TaskType.UNKNOWN,
            phase=Phase.UNKNOWN,
            reasoning="Fallback to safe defaults",
            is_mechanical=False,
            quality_critical=False,
            needs_tools=True,
        )

    @staticmethod
    def quick_select(task_type: TaskType) -> SelectionResult:
        """
        Quick selection without calling classifier.

        Use when task type is already known (e.g., from tool invocation).
        """
        model = TASK_TYPE_MODELS.get(task_type, "sonnet")
        thinking = TASK_TYPE_THINKING.get(task_type, 4000)

        return SelectionResult(
            model=model,
            model_id=MODELS[model].model_id,
            thinking_budget=thinking,
            task_type=task_type,
            phase=Phase.UNKNOWN,
            reasoning=f"Quick selection for {task_type.value}",
            is_mechanical=task_type in (
                TaskType.FILE_READ,
                TaskType.FILE_SEARCH,
                TaskType.LIST_FILES,
                TaskType.FORMAT_CODE,
                TaskType.RUN_COMMAND,
            ),
            quality_critical=task_type in (
                TaskType.PLANNING,
                TaskType.ARCHITECTURE,
                TaskType.STRATEGY,
                TaskType.REVIEW,
            ),
            needs_tools=task_type not in (TaskType.STRATEGY, TaskType.REVIEW),
        )
