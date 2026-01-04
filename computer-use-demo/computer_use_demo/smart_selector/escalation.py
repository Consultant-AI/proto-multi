"""
Adaptive Escalation for Smart Model Selection.

Provides mechanisms to escalate to stronger models when:
1. Initial response has low confidence
2. Task turns out to be more complex than expected
3. Errors or failures occur
"""

from dataclasses import dataclass
from typing import Callable

from .models import MODELS, OPUS_4_5, SONNET_4_5, Phase, SelectionResult, TaskType


@dataclass
class ExecutionResult:
    """Result of task execution."""

    success: bool
    output: str | None = None
    error: str | None = None
    confidence: float = 1.0  # 0.0 to 1.0
    needs_more_reasoning: bool = False
    should_escalate: bool = False


class AdaptiveExecutor:
    """
    Executes tasks with adaptive escalation.

    Starts with the recommended model, but escalates to stronger
    models when needed for quality.
    """

    def __init__(self, executor_func: Callable | None = None):
        """
        Initialize with optional executor function.

        Args:
            executor_func: Function that executes tasks with given selection
                           Signature: async (task, selection) -> ExecutionResult
        """
        self.executor_func = executor_func
        self.escalation_history: list[SelectionResult] = []

    async def execute(
        self,
        task: str,
        initial_selection: SelectionResult,
        max_escalations: int = 2,
    ) -> tuple[ExecutionResult, SelectionResult]:
        """
        Execute task with adaptive escalation.

        Args:
            task: The task to execute
            initial_selection: Initial model selection
            max_escalations: Maximum number of escalation attempts

        Returns:
            Tuple of (result, final_selection)
        """
        if not self.executor_func:
            raise ValueError("No executor function provided")

        current_selection = initial_selection
        self.escalation_history = [current_selection]

        for attempt in range(max_escalations + 1):
            result = await self.executor_func(task, current_selection)

            if result.success and not result.should_escalate:
                # Task completed successfully
                return result, current_selection

            if result.needs_more_reasoning or result.should_escalate:
                # Try escalating
                escalated = self.escalate(current_selection)

                if escalated.model == current_selection.model and \
                   escalated.thinking_budget == current_selection.thinking_budget:
                    # Already at max - return best effort
                    return result, current_selection

                current_selection = escalated
                self.escalation_history.append(escalated)
                print(f"[Escalation] Attempt {attempt + 1}: {escalated.model} "
                      f"with {escalated.thinking_budget} thinking tokens")
            else:
                # Failed but shouldn't escalate - return result
                return result, current_selection

        # Max escalations reached
        return result, current_selection

    def escalate(self, current: SelectionResult) -> SelectionResult:
        """
        Escalate to a stronger model or more thinking.

        Escalation order:
        1. Increase thinking budget (if below max)
        2. Upgrade model (haiku → sonnet → opus)
        """
        # First: try increasing thinking
        if current.thinking_budget < 10000:
            return SelectionResult(
                model=current.model,
                model_id=current.model_id,
                thinking_budget=10000,
                task_type=current.task_type,
                phase=current.phase,
                reasoning=f"Escalated thinking: {current.thinking_budget} → 10000",
                is_mechanical=False,
                quality_critical=True,
                needs_tools=current.needs_tools,
            )

        # Second: try upgrading model
        if current.model == "haiku":
            return SelectionResult(
                model="sonnet",
                model_id=SONNET_4_5.model_id,
                thinking_budget=current.thinking_budget,
                task_type=current.task_type,
                phase=current.phase,
                reasoning=f"Escalated model: haiku → sonnet",
                is_mechanical=False,
                quality_critical=True,
                needs_tools=current.needs_tools,
            )

        if current.model == "sonnet" and current.thinking_budget < 10000:
            return SelectionResult(
                model="sonnet",
                model_id=SONNET_4_5.model_id,
                thinking_budget=10000,
                task_type=current.task_type,
                phase=current.phase,
                reasoning="Escalated thinking: → 10000 (max)",
                is_mechanical=False,
                quality_critical=True,
                needs_tools=current.needs_tools,
            )

        if current.model == "sonnet":
            return SelectionResult(
                model="opus",
                model_id=OPUS_4_5.model_id,
                thinking_budget=10000,
                task_type=current.task_type,
                phase=current.phase,
                reasoning="Escalated model: sonnet → opus (max)",
                is_mechanical=False,
                quality_critical=True,
                needs_tools=current.needs_tools,
            )

        # Already at max (opus with 10000) - return unchanged
        return current

    @staticmethod
    def should_escalate_on_error(error: str) -> bool:
        """
        Determine if an error warrants escalation.

        Some errors indicate the model needs more capability.
        """
        escalation_indicators = [
            "i don't understand",
            "i'm not sure",
            "could you clarify",
            "this is complex",
            "need more context",
            "ambiguous",
            "multiple interpretations",
            "beyond my capability",
        ]

        error_lower = error.lower()
        return any(indicator in error_lower for indicator in escalation_indicators)

    @staticmethod
    def estimate_confidence(response: str) -> float:
        """
        Estimate confidence from response text.

        Low confidence phrases reduce the score.
        """
        low_confidence_phrases = [
            "i think",
            "maybe",
            "perhaps",
            "not sure",
            "might be",
            "could be",
            "possibly",
            "unclear",
            "i believe",
            "i assume",
        ]

        high_confidence_phrases = [
            "definitely",
            "certainly",
            "clearly",
            "this is",
            "the answer is",
            "here's the solution",
        ]

        response_lower = response.lower()

        low_count = sum(1 for p in low_confidence_phrases if p in response_lower)
        high_count = sum(1 for p in high_confidence_phrases if p in response_lower)

        # Start at 0.8 (default confidence)
        confidence = 0.8

        # Reduce for low confidence phrases
        confidence -= low_count * 0.1

        # Increase for high confidence phrases
        confidence += high_count * 0.05

        # Clamp to 0.0-1.0
        return max(0.0, min(1.0, confidence))


def get_escalation_path(current: SelectionResult) -> list[SelectionResult]:
    """
    Get the full escalation path from current selection to max.

    Useful for debugging and cost estimation.
    """
    path = [current]
    executor = AdaptiveExecutor()

    while True:
        escalated = executor.escalate(path[-1])
        if (escalated.model == path[-1].model and
            escalated.thinking_budget == path[-1].thinking_budget):
            break
        path.append(escalated)

    return path


def estimate_total_cost(selections: list[SelectionResult], avg_tokens: int = 2000) -> float:
    """
    Estimate total cost for a list of selections.

    Args:
        selections: List of SelectionResult objects
        avg_tokens: Average input/output tokens per call

    Returns:
        Estimated cost in dollars
    """
    total = 0.0

    for selection in selections:
        config = MODELS[selection.model]

        # Input cost
        input_cost = (avg_tokens / 1_000_000) * config.input_cost_per_mtok

        # Output cost (including thinking)
        output_tokens = avg_tokens + selection.thinking_budget
        output_cost = (output_tokens / 1_000_000) * config.output_cost_per_mtok

        total += input_cost + output_cost

    return total
