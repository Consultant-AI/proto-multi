"""
Classifier prompts for Smart Model Selection.

Philosophy: "Would Opus produce a DIFFERENT or BETTER result?"
Only use weaker models when the result would be IDENTICAL.

IMPORTANT: Selection is purely CONTENT-BASED.
The classifier analyzes the actual task text to determine complexity.
No hardcoded rules based on phase, agent type, or labels.
"""

# Main classifier prompt - fully content-based approach
CLASSIFIER_PROMPT = """Analyze this task and determine the optimal Claude model and thinking budget.

PHILOSOPHY: Act like Opus is always on. Only recommend weaker models when
the result would be IDENTICAL (zero quality difference).

Task: {task}
Context: {context}

COMPANY HIERARCHY:
- OPUS = CEO: Strategic decisions, ambiguity, architecture, planning, complex multi-step
- SONNET = Senior Engineer: Implementation, debugging, quality code, moderate complexity
- HAIKU = Junior/Automation: ONLY mechanical tasks (identical results guaranteed)

DECISION FRAMEWORK - Analyze the ACTUAL TASK CONTENT:

1. Is this task MECHANICAL (file read, search, list, format, simple command)?
   → Haiku is fine, Opus would produce IDENTICAL result
   Examples: "read file X", "list all .py files", "format this JSON"

2. Does the task require ANY of these?
   - Judgment, interpretation, ambiguity resolution → Opus
   - Strategic thinking or planning → Opus
   - Architecture or design decisions → Opus
   - Multi-step planning or coordination → Opus
   - Quality-critical code → Sonnet
   - Complex debugging or investigation → Sonnet
   - Creative problem-solving → Sonnet
   - Security considerations → Sonnet
   - Refactoring or significant changes → Sonnet

3. Key question: Would Opus produce a DIFFERENT or BETTER result?
   → If yes, use Opus/Sonnet (the stronger model matters)
   → If no (identical result guaranteed), Haiku is fine

THINKING BUDGET GUIDE:
- 0: Mechanical tasks, no reasoning needed
- 4000: Simple implementation, following clear instructions
- 10000: Complex tasks, architecture, strategy, planning, debugging (MAX)

Return ONLY valid JSON (no markdown, no explanation):
{{"model": "haiku|sonnet|opus", "thinking_budget": 0|4000|10000, "task_type": "file_read|file_search|list_files|format_code|run_command|simple_code|feature_implementation|bug_fix|refactor|debugging|planning|architecture|design|strategy|review|unknown", "is_mechanical": true|false, "quality_critical": true|false, "needs_tools": true|false, "reasoning": "brief explanation of why this model/budget based on task content"}}"""


# Quick classifier for obvious mechanical tasks (uses less tokens)
QUICK_CLASSIFIER_PROMPT = """Classify this task. Is it MECHANICAL (Haiku) or needs INTELLIGENCE (Sonnet/Opus)?

Task: {task}

MECHANICAL = file read, search, list, format, run simple command (result would be identical)
INTELLIGENCE = any judgment, coding, planning, debugging, design, ambiguity (result would differ)

Return ONLY valid JSON:
{{"model": "haiku|sonnet|opus", "thinking_budget": 0|4000|10000, "is_mechanical": true|false, "reasoning": "brief"}}"""


# Fallback - when classifier fails, use safe defaults (Sonnet = safe middle ground)
FALLBACK_SELECTION = {
    "model": "sonnet",
    "thinking_budget": 4000,
    "task_type": "unknown",
    "is_mechanical": False,
    "quality_critical": False,
    "needs_tools": True,
    "reasoning": "Fallback to safe defaults",
}


def format_classifier_prompt(
    task: str,
    context: dict | None = None,
) -> str:
    """Format the classifier prompt with task details.

    Selection is purely content-based - only the task text and context matter.
    No phase-based routing or hardcoded rules.
    """
    context = context or {}
    context_str = ", ".join(f"{k}: {v}" for k, v in context.items()) if context else "None"

    return CLASSIFIER_PROMPT.format(
        task=task,
        context=context_str,
    )
