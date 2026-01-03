"""
Data models and configurations for Smart Model Selection.

Model Hierarchy (Company CEO Model):
- OPUS = CEO: Strategic decisions, ambiguity resolution, architecture
- SONNET = Senior Engineers: Complex implementation, debugging, quality code
- HAIKU = Junior Staff: ONLY mechanical tasks (file ops, searches)
"""

from dataclasses import dataclass, field
from typing import Literal
from enum import Enum


class TaskType(str, Enum):
    """Classification of task types."""

    # Mechanical tasks - Haiku is sufficient
    FILE_READ = "file_read"
    FILE_SEARCH = "file_search"
    LIST_FILES = "list_files"
    FORMAT_CODE = "format_code"
    RUN_COMMAND = "run_command"

    # Implementation tasks - Sonnet recommended
    SIMPLE_CODE = "simple_code"
    FEATURE_IMPL = "feature_implementation"
    BUG_FIX = "bug_fix"
    REFACTOR = "refactor"
    DEBUGGING = "debugging"

    # Strategic tasks - Opus recommended
    PLANNING = "planning"
    ARCHITECTURE = "architecture"
    DESIGN = "design"
    STRATEGY = "strategy"
    REVIEW = "review"

    # Unknown - defaults to Sonnet with moderate thinking
    UNKNOWN = "unknown"


class Phase(str, Enum):
    """Execution phase - for metadata/logging only, NOT used for model selection.

    Model selection is purely content-based - the classifier analyzes the actual
    task content to determine complexity, not the phase.
    """

    PLANNING = "planning"
    TASK_BREAKDOWN = "task_breakdown"
    STRATEGY = "strategy"
    REVIEW = "review"
    EXECUTION = "execution"
    IMPLEMENTATION = "implementation"
    VERIFICATION = "verification"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class ModelConfig:
    """Configuration for a Claude model."""

    model_id: str
    name: str
    input_cost_per_mtok: float  # $ per million input tokens
    output_cost_per_mtok: float  # $ per million output tokens
    supports_thinking: bool
    max_thinking_tokens: int

    # Capability ratings (1-10)
    reasoning_capability: int
    coding_capability: int
    creativity_capability: int


# Current model configurations (Dec 2024 / Jan 2025)
HAIKU_4_5 = ModelConfig(
    model_id="claude-haiku-4-5-20251001",
    name="Claude Haiku 4.5",
    input_cost_per_mtok=1.0,
    output_cost_per_mtok=5.0,
    supports_thinking=True,
    max_thinking_tokens=31999,
    reasoning_capability=6,
    coding_capability=6,
    creativity_capability=5,
)

SONNET_4_5 = ModelConfig(
    model_id="claude-sonnet-4-5-20250929",
    name="Claude Sonnet 4.5",
    input_cost_per_mtok=3.0,
    output_cost_per_mtok=15.0,
    supports_thinking=True,
    max_thinking_tokens=31999,
    reasoning_capability=8,
    coding_capability=9,
    creativity_capability=8,
)

OPUS_4_5 = ModelConfig(
    model_id="claude-opus-4-5-20251101",
    name="Claude Opus 4.5",
    input_cost_per_mtok=5.0,
    output_cost_per_mtok=25.0,
    supports_thinking=True,
    max_thinking_tokens=31999,
    reasoning_capability=10,
    coding_capability=10,
    creativity_capability=10,
)

# Model lookup by name
MODELS = {
    "haiku": HAIKU_4_5,
    "sonnet": SONNET_4_5,
    "opus": OPUS_4_5,
}


@dataclass
class SelectionResult:
    """Result from the SmartSelector."""

    model: Literal["haiku", "sonnet", "opus"]
    model_id: str
    thinking_budget: int  # 0, 4000, 10000, or 31999
    task_type: TaskType
    phase: Phase

    # Reasoning for the selection
    reasoning: str

    # Flags
    is_mechanical: bool  # True = no intelligence needed
    quality_critical: bool  # True = must use strongest model
    needs_tools: bool

    # Cost estimate (rough)
    estimated_cost: float = 0.0

    def get_model_config(self) -> ModelConfig:
        """Get the full model configuration."""
        return MODELS[self.model]

    def to_dict(self) -> dict:
        """Convert to dictionary for logging."""
        return {
            "model": self.model,
            "model_id": self.model_id,
            "thinking_budget": self.thinking_budget,
            "task_type": self.task_type.value,
            "phase": self.phase.value,
            "reasoning": self.reasoning,
            "is_mechanical": self.is_mechanical,
            "quality_critical": self.quality_critical,
            "needs_tools": self.needs_tools,
            "estimated_cost": self.estimated_cost,
        }


# NOTE: Phase-based defaults have been removed.
# Model selection is now purely content-based - the Haiku classifier
# analyzes the actual task content to determine model and thinking budget.
# This ensures decisions are dynamic, not hardcoded by phase labels.


# Task type to model mapping (capability-first)
TASK_TYPE_MODELS = {
    # Mechanical tasks - Haiku sufficient
    TaskType.FILE_READ: "haiku",
    TaskType.FILE_SEARCH: "haiku",
    TaskType.LIST_FILES: "haiku",
    TaskType.FORMAT_CODE: "haiku",
    TaskType.RUN_COMMAND: "haiku",

    # Implementation tasks - Sonnet
    TaskType.SIMPLE_CODE: "sonnet",
    TaskType.FEATURE_IMPL: "sonnet",
    TaskType.BUG_FIX: "sonnet",
    TaskType.REFACTOR: "sonnet",
    TaskType.DEBUGGING: "sonnet",

    # Strategic tasks - Opus
    TaskType.PLANNING: "opus",
    TaskType.ARCHITECTURE: "opus",
    TaskType.DESIGN: "opus",
    TaskType.STRATEGY: "opus",
    TaskType.REVIEW: "opus",

    # Unknown - Sonnet as safe default
    TaskType.UNKNOWN: "sonnet",
}


# Task type to thinking budget mapping
TASK_TYPE_THINKING = {
    # Mechanical - no thinking needed
    TaskType.FILE_READ: 0,
    TaskType.FILE_SEARCH: 0,
    TaskType.LIST_FILES: 0,
    TaskType.FORMAT_CODE: 0,
    TaskType.RUN_COMMAND: 0,

    # Implementation - moderate thinking
    TaskType.SIMPLE_CODE: 4000,
    TaskType.FEATURE_IMPL: 4000,
    TaskType.BUG_FIX: 4000,
    TaskType.REFACTOR: 4000,
    TaskType.DEBUGGING: 10000,  # Debugging needs more

    # Strategic - maximum thinking
    TaskType.PLANNING: 10000,
    TaskType.ARCHITECTURE: 31999,
    TaskType.DESIGN: 10000,
    TaskType.STRATEGY: 31999,
    TaskType.REVIEW: 10000,

    # Unknown - moderate thinking
    TaskType.UNKNOWN: 4000,
}
