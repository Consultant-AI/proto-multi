"""
Type definitions for Self-Improvement Engine.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any
import uuid


class ModificationType(str, Enum):
    """Types of self-modifications."""
    CODE_CHANGE = "code_change"
    AGENT_CREATE = "agent_create"
    AGENT_UPDATE = "agent_update"
    TOOL_CREATE = "tool_create"
    SKILL_CREATE = "skill_create"
    CONFIG_CHANGE = "config_change"


class ModificationStatus(str, Enum):
    """Status of a modification."""
    PENDING = "pending"
    TESTING = "testing"
    APPROVED = "approved"
    APPLIED = "applied"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"
    REJECTED = "rejected"


@dataclass
class SafetyCheck:
    """Result of a safety check."""
    name: str
    passed: bool
    message: str = ""
    severity: str = "warning"  # info, warning, error


@dataclass
class Modification:
    """A self-improvement modification."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: ModificationType = ModificationType.CODE_CHANGE
    status: ModificationStatus = ModificationStatus.PENDING

    # What's being modified
    target: str = ""  # File path or component name
    description: str = ""

    # The actual changes
    changes: dict[str, Any] = field(default_factory=dict)

    # For rollback
    backup: dict[str, Any] = field(default_factory=dict)

    # Safety checks
    safety_checks: list[SafetyCheck] = field(default_factory=list)

    # Test results
    test_results: dict[str, Any] = field(default_factory=dict)

    # Approval
    requires_approval: bool = False
    approved_by: str | None = None
    approved_at: datetime | None = None

    # Timestamps
    created_at: datetime = field(default_factory=datetime.utcnow)
    applied_at: datetime | None = None

    # Reason for modification
    reason: str = ""

    # Source (what triggered this)
    source: str = ""  # pattern_detection, user_request, error_analysis

    def is_safe(self) -> bool:
        """Check if all safety checks passed."""
        return all(c.passed for c in self.safety_checks if c.severity == "error")

    def can_apply(self) -> bool:
        """Check if modification can be applied."""
        if self.status != ModificationStatus.APPROVED:
            return False
        if not self.is_safe():
            return False
        if self.requires_approval and not self.approved_by:
            return False
        return True


@dataclass
class AgentSpec:
    """Specification for a new agent."""
    name: str
    display_name: str = ""
    description: str = ""

    # What the agent can do
    capabilities: list[str] = field(default_factory=list)

    # System prompt template
    system_prompt: str = ""

    # Tools the agent can use
    tools: list[str] = field(default_factory=list)

    # Skills to load
    skills: list[str] = field(default_factory=list)

    # Model preferences
    model: str = "claude-sonnet-4-20250514"
    thinking_budget: int = 0

    # Delegation
    can_delegate: bool = True
    delegate_to: list[str] = field(default_factory=list)

    # Custom metadata
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ToolSpec:
    """Specification for a compound tool."""
    name: str
    display_name: str = ""
    description: str = ""

    # Input parameters
    parameters: list[dict[str, Any]] = field(default_factory=list)

    # Steps to execute
    steps: list[dict[str, Any]] = field(default_factory=list)

    # Output format
    output_format: str = "text"  # text, json, file

    # Safety constraints
    max_runtime: float = 60.0
    requires_confirmation: bool = False

    # Examples for documentation
    examples: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class SkillSpec:
    """Specification for a generated skill."""
    name: str
    display_name: str = ""
    description: str = ""

    # Trigger conditions
    triggers: dict[str, list[str]] = field(default_factory=dict)

    # Content sections
    sections: list[dict[str, str]] = field(default_factory=list)

    # Source patterns used
    patterns: list[str] = field(default_factory=list)

    # Generated from
    generated_from: str = ""  # code_analysis, pattern_mining, user_request

    # Confidence score
    confidence: float = 0.0


@dataclass
class ImprovementSuggestion:
    """A suggestion for system improvement."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    description: str = ""
    type: ModificationType = ModificationType.CODE_CHANGE
    priority: str = "medium"  # low, medium, high
    confidence: float = 0.0

    # What triggered this suggestion
    source: str = ""
    evidence: list[str] = field(default_factory=list)

    # Impact assessment
    estimated_impact: str = ""
    risk_level: str = "low"  # low, medium, high

    # Implementation details
    implementation: dict[str, Any] = field(default_factory=dict)

    created_at: datetime = field(default_factory=datetime.utcnow)
