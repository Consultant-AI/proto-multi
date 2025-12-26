"""
Specification Template and Checklist for Proto Multi-Agent System.

This module defines the standard specification workflow that agents must follow
before implementing any task. Based on Auto-Claude's spec-first methodology.
"""

# Standard Specification Checklist
SPECIFICATION_CHECKLIST = [
    "Understand the problem context and requirements",
    "Identify affected files and components",
    "Define clear acceptance criteria",
    "List implementation steps in order",
    "Identify potential risks and edge cases",
    "Plan test strategy and test cases",
    "Document any assumptions or dependencies",
    "Review specification for completeness",
]

# Specification Template
SPEC_TEMPLATE = """
# Task Specification: {task_title}

## 1. Context & Problem Statement
**What needs to be done and why?**
{context}

## 2. Current State Analysis
**What is the current state of the codebase related to this task?**
- Files involved: {files}
- Current behavior: {current_behavior}
- Dependencies: {dependencies}

## 3. Acceptance Criteria
**What must be true for this task to be considered complete?**
{acceptance_criteria}

## 4. Implementation Plan
**Step-by-step plan for implementing this task:**
{implementation_steps}

## 5. Test Strategy
**How will we verify this works correctly?**
- Unit tests: {unit_tests}
- Integration tests: {integration_tests}
- Manual testing: {manual_tests}

## 6. Risks & Edge Cases
**What could go wrong? What edge cases need to be handled?**
{risks}

## 7. Assumptions & Dependencies
**What are we assuming? What does this task depend on?**
{assumptions}
"""

# Discovery Phase Questions (inspired by Auto-Claude's 3-8 phases)
DISCOVERY_QUESTIONS = [
    # Phase 1: Understanding
    "What is the specific problem we're solving?",
    "Who are the stakeholders and what do they need?",
    "What are the constraints (time, resources, technical)?",

    # Phase 2: Analysis
    "What files and components are affected?",
    "What is the current implementation (if any)?",
    "What are the dependencies and interactions?",

    # Phase 3: Design
    "What approach will we take to solve this?",
    "What are the alternatives and trade-offs?",
    "How does this fit with the existing architecture?",

    # Phase 4: Planning
    "What are the specific steps to implement this?",
    "What order should these steps be done in?",
    "What can be done in parallel vs. sequentially?",

    # Phase 5: Testing
    "How will we test each component?",
    "What are the critical test cases?",
    "What edge cases need coverage?",

    # Phase 6: Risk Assessment
    "What could go wrong during implementation?",
    "What are the technical risks?",
    "What is the rollback strategy if needed?",
]

# Specification Validation Rules
SPEC_VALIDATION_RULES = {
    "context": "Must provide clear problem statement and context",
    "acceptance_criteria": "Must have at least 1 testable criterion",
    "implementation_checklist": "Must have at least 3 implementation steps",
    "files_identified": "Must identify affected files/components",
    "test_strategy": "Must define how changes will be verified",
}


def validate_specification(spec_data: dict) -> tuple[bool, list[str]]:
    """
    Validate that a specification meets minimum requirements.

    Args:
        spec_data: Dictionary containing specification fields

    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []

    # Check context
    if not spec_data.get("context") or len(spec_data["context"]) < 20:
        errors.append("Context must be at least 20 characters")

    # Check acceptance criteria
    criteria = spec_data.get("acceptance_criteria", [])
    if not criteria or len(criteria) < 1:
        errors.append("Must have at least 1 acceptance criterion")

    # Check implementation checklist
    checklist = spec_data.get("implementation_checklist", [])
    if not checklist or len(checklist) < 3:
        errors.append("Must have at least 3 implementation steps")

    return len(errors) == 0, errors


def get_spec_template_filled(
    task_title: str,
    context: str = "",
    files: str = "",
    current_behavior: str = "",
    dependencies: str = "",
    acceptance_criteria: list[str] = None,
    implementation_steps: list[str] = None,
    unit_tests: str = "",
    integration_tests: str = "",
    manual_tests: str = "",
    risks: str = "",
    assumptions: str = "",
) -> str:
    """
    Generate a filled specification template.

    Args:
        task_title: Title of the task
        context: Context and problem statement
        files: Files involved
        current_behavior: Current state of the code
        dependencies: Dependencies
        acceptance_criteria: List of acceptance criteria
        implementation_steps: List of implementation steps
        unit_tests: Unit test strategy
        integration_tests: Integration test strategy
        manual_tests: Manual test strategy
        risks: Risks and edge cases
        assumptions: Assumptions and dependencies

    Returns:
        Formatted specification string
    """
    # Format lists
    criteria_text = "\n".join([f"- {c}" for c in (acceptance_criteria or [])])
    steps_text = "\n".join([f"{i+1}. {s}" for i, s in enumerate(implementation_steps or [])])

    return SPEC_TEMPLATE.format(
        task_title=task_title,
        context=context or "[To be filled]",
        files=files or "[To be identified]",
        current_behavior=current_behavior or "[To be analyzed]",
        dependencies=dependencies or "[To be identified]",
        acceptance_criteria=criteria_text or "[To be defined]",
        implementation_steps=steps_text or "[To be planned]",
        unit_tests=unit_tests or "[To be planned]",
        integration_tests=integration_tests or "[To be planned]",
        manual_tests=manual_tests or "[To be planned]",
        risks=risks or "[To be identified]",
        assumptions=assumptions or "[To be documented]",
    )
