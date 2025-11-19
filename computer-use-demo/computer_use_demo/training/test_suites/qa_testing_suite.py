"""
Test Suite for QA Testing Agent.

This module contains test cases for evaluating the QA Testing specialist agent's
ability to create test plans, write test cases, identify edge cases, and report bugs.
"""

from computer_use_demo.training import TestCase, TestSuite


def score_test_plan(output: str) -> float:
    """Score test plan quality."""
    score = 0.0
    output_lower = output.lower()

    # Test scope and objectives (20 points)
    if "scope" in output_lower or "objective" in output_lower:
        score += 10
    if "test strategy" in output_lower or "approach" in output_lower:
        score += 10

    # Test types coverage (20 points)
    test_types = ["functional", "integration", "performance", "security", "usability"]
    found_types = sum(1 for t in test_types if t in output_lower)
    score += min(20, found_types * 5)

    # Test environment (15 points)
    if "environment" in output_lower or "setup" in output_lower:
        score += 10
    if "test data" in output_lower or "data" in output_lower:
        score += 5

    # Entry/exit criteria (15 points)
    if "entry criteria" in output_lower or "prerequisites" in output_lower:
        score += 7.5
    if "exit criteria" in output_lower or "completion" in output_lower:
        score += 7.5

    # Deliverables and timeline (15 points)
    if "deliverable" in output_lower or "artifact" in output_lower:
        score += 7.5
    if "timeline" in output_lower or "schedule" in output_lower:
        score += 7.5

    # Risk and dependencies (15 points)
    if "risk" in output_lower or "assumption" in output_lower:
        score += 7.5
    if "dependencies" in output_lower or "blocker" in output_lower:
        score += 7.5

    return min(100, score)


def score_test_cases(output: str) -> float:
    """Score test case creation."""
    score = 0.0
    output_lower = output.lower()

    # Test case structure (25 points)
    if "test id" in output_lower or "tc-" in output_lower or "test case id" in output_lower:
        score += 10
    if "precondition" in output_lower or "pre-condition" in output_lower:
        score += 7.5
    if "expected result" in output_lower or "expected outcome" in output_lower:
        score += 7.5

    # Test steps (25 points)
    if "step" in output_lower or "action" in output_lower:
        score += 15
    if "given" in output_lower and "when" in output_lower and "then" in output_lower:
        score += 10  # Bonus for BDD format

    # Coverage (25 points)
    if "positive" in output_lower or "happy path" in output_lower:
        score += 10
    if "negative" in output_lower or "error" in output_lower:
        score += 10
    if "boundary" in output_lower or "edge case" in output_lower:
        score += 5

    # Test data (15 points)
    if "test data" in output_lower or "input" in output_lower:
        score += 10
    if "valid" in output_lower and "invalid" in output_lower:
        score += 5

    # Priority and severity (10 points)
    if "priority" in output_lower or "critical" in output_lower or "high" in output_lower:
        score += 5
    if "severity" in output_lower:
        score += 5

    return min(100, score)


def score_edge_cases(output: str) -> float:
    """Score edge case identification."""
    score = 0.0
    output_lower = output.lower()

    # Boundary conditions (25 points)
    boundary_terms = ["boundary", "limit", "maximum", "minimum", "threshold", "zero", "empty"]
    found_boundary = sum(1 for term in boundary_terms if term in output_lower)
    score += min(25, found_boundary * 4)

    # Invalid inputs (20 points)
    invalid_terms = ["invalid", "null", "negative", "special character", "injection"]
    found_invalid = sum(1 for term in invalid_terms if term in output_lower)
    score += min(20, found_invalid * 5)

    # Concurrent/timing issues (15 points)
    timing_terms = ["concurrent", "race condition", "timeout", "delay", "timing"]
    found_timing = sum(1 for term in timing_terms if term in output_lower)
    score += min(15, found_timing * 5)

    # State transitions (15 points)
    state_terms = ["state", "transition", "sequence", "order"]
    found_state = sum(1 for term in state_terms if term in output_lower)
    score += min(15, found_state * 5)

    # Security edge cases (15 points)
    security_terms = ["security", "authentication", "authorization", "xss", "sql injection"]
    found_security = sum(1 for term in security_terms if term in output_lower)
    score += min(15, found_security * 5)

    # Completeness (10 points)
    if len(output) > 500:  # Detailed analysis
        score += 10

    return min(100, score)


def score_bug_report(output: str) -> float:
    """Score bug report quality."""
    score = 0.0
    output_lower = output.lower()

    # Title/summary (15 points)
    if len(output.split("\n")[0]) > 20:  # Has a descriptive title
        score += 15

    # Steps to reproduce (25 points)
    if "steps to reproduce" in output_lower or "reproduce" in output_lower:
        score += 15
    if output_lower.count("step") >= 3 or output_lower.count("1.") >= 3:
        score += 10

    # Expected vs actual (20 points)
    if "expected" in output_lower:
        score += 10
    if "actual" in output_lower:
        score += 10

    # Environment details (15 points)
    env_terms = ["environment", "browser", "os", "version", "device"]
    found_env = sum(1 for term in env_terms if term in output_lower)
    score += min(15, found_env * 5)

    # Severity/priority (10 points)
    if "severity" in output_lower or "priority" in output_lower:
        score += 5
    if any(term in output_lower for term in ["critical", "high", "medium", "low", "blocker"]):
        score += 5

    # Impact (10 points)
    if "impact" in output_lower or "affect" in output_lower or "user" in output_lower:
        score += 10

    # Attachments/evidence (5 points)
    if "screenshot" in output_lower or "log" in output_lower or "video" in output_lower:
        score += 5

    return min(100, score)


def score_automation_strategy(output: str) -> float:
    """Score test automation strategy."""
    score = 0.0
    output_lower = output.lower()

    # Test selection criteria (20 points)
    if "automate" in output_lower and "manual" in output_lower:
        score += 10
    if "roi" in output_lower or "cost" in output_lower or "benefit" in output_lower:
        score += 10

    # Framework recommendation (20 points)
    frameworks = ["selenium", "cypress", "playwright", "junit", "pytest", "testng"]
    if any(fw in output_lower for fw in frameworks):
        score += 15
    if "framework" in output_lower:
        score += 5

    # Test pyramid/strategy (20 points)
    if "unit test" in output_lower or "unit" in output_lower:
        score += 7
    if "integration" in output_lower:
        score += 7
    if "e2e" in output_lower or "end-to-end" in output_lower or "ui test" in output_lower:
        score += 6

    # Implementation approach (15 points)
    if "page object" in output_lower or "design pattern" in output_lower:
        score += 7.5
    if "data-driven" in output_lower or "keyword-driven" in output_lower:
        score += 7.5

    # CI/CD integration (15 points)
    if "ci/cd" in output_lower or "continuous" in output_lower or "pipeline" in output_lower:
        score += 10
    if "jenkins" in output_lower or "github actions" in output_lower or "gitlab" in output_lower:
        score += 5

    # Reporting and maintenance (10 points)
    if "report" in output_lower or "result" in output_lower:
        score += 5
    if "maintain" in output_lower or "update" in output_lower:
        score += 5

    return min(100, score)


def create_qa_testing_test_suite() -> TestSuite:
    """Create comprehensive test suite for QA Testing agent."""
    suite = TestSuite(
        name="QA Testing Agent Tests",
        agent_type="qa-testing",
        metadata={"version": "1.0", "created": "2025-01-19"},
    )

    # Test 1: Create test plan
    suite.add_test(
        TestCase(
            name="Create Test Plan for E-commerce Checkout",
            task="""Create a comprehensive test plan for testing an e-commerce checkout flow that includes:
        - Shopping cart
        - Payment processing
        - Order confirmation
        - Email notifications

        Include test scope, strategy, types of testing, environment requirements,
        entry/exit criteria, and risk analysis.""",
            success_criteria=score_test_plan,
            metadata={"difficulty": "medium", "category": "test_planning"},
        )
    )

    # Test 2: Write test cases
    suite.add_test(
        TestCase(
            name="Write Test Cases for User Registration",
            task="""Write 5 detailed test cases for a user registration feature with these fields:
        - Email (required, must be valid format)
        - Password (required, min 8 chars, must include number and special char)
        - Confirm Password (must match password)
        - Terms & Conditions checkbox (required)

        Include positive, negative, and boundary test cases with clear steps,
        expected results, and test data.""",
            success_criteria=score_test_cases,
            metadata={"difficulty": "medium", "category": "test_cases"},
        )
    )

    # Test 3: Identify edge cases
    suite.add_test(
        TestCase(
            name="Identify Edge Cases for Search Feature",
            task="""Identify at least 10 edge cases for a product search feature that includes:
        - Text search with autocomplete
        - Filters (price range, category, rating)
        - Sorting options
        - Pagination

        Consider boundary conditions, invalid inputs, concurrent users,
        special characters, and performance edge cases.""",
            success_criteria=score_edge_cases,
            metadata={"difficulty": "hard", "category": "edge_cases"},
        )
    )

    # Test 4: Write bug report
    suite.add_test(
        TestCase(
            name="Write Bug Report for Payment Failure",
            task="""Write a detailed bug report for this scenario:
        When a user tries to complete a purchase with a valid credit card,
        the payment fails with error "Transaction declined" even though the card is valid
        and has sufficient funds. This happens intermittently (about 30% of the time).

        Include all necessary details for a developer to investigate and fix the issue.""",
            success_criteria=score_bug_report,
            metadata={"difficulty": "easy", "category": "bug_reporting"},
        )
    )

    # Test 5: Create automation strategy
    suite.add_test(
        TestCase(
            name="Design Test Automation Strategy",
            task="""Design a test automation strategy for a new SaaS application with:
        - Web application (React frontend)
        - REST API backend
        - Mobile app (iOS/Android)

        Recommend frameworks, what to automate vs manual test, test pyramid approach,
        CI/CD integration, and maintenance strategy. Justify your recommendations.""",
            success_criteria=score_automation_strategy,
            metadata={"difficulty": "hard", "category": "automation"},
        )
    )

    return suite


# Export the test suite
qa_testing_suite = create_qa_testing_test_suite()
