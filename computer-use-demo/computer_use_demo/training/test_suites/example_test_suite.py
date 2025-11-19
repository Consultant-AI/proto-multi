"""
Example Test Suite for Product Manager Agent.

This demonstrates how to create test cases for agent training.
"""

from computer_use_demo.agents import ProductManagerAgent
from computer_use_demo.training import TestCase, TestSuite


def score_user_stories(output: str) -> float:
    """
    Score user story quality.

    Criteria:
    - Contains "As a" (user persona) - 20 points
    - Contains "I want" (action) - 20 points
    - Contains "so that" (value/reason) - 20 points
    - Has acceptance criteria - 20 points
    - Includes priority/estimate - 20 points
    """
    score = 0.0
    output_lower = output.lower()

    if "as a" in output_lower or "as an" in output_lower:
        score += 20
    if "i want" in output_lower or "i need" in output_lower:
        score += 20
    if "so that" in output_lower or "in order to" in output_lower:
        score += 20
    if "acceptance criteria" in output_lower or "given" in output_lower:
        score += 20
    if any(word in output_lower for word in ["priority", "points", "estimate", "high", "medium", "low"]):
        score += 20

    return score


def score_feature_prioritization(output: str) -> float:
    """
    Score feature prioritization quality.

    Criteria:
    - Lists multiple features - 25 points
    - Provides rationale - 25 points
    - Considers impact/effort - 25 points
    - Clear recommendation - 25 points
    """
    score = 0.0
    output_lower = output.lower()

    # Count features mentioned
    feature_count = output.count("\n-") + output.count("\n*") + output.count("\n1.")
    if feature_count >= 3:
        score += 25

    if any(word in output_lower for word in ["because", "since", "rationale", "reason"]):
        score += 25

    if any(word in output_lower for word in ["impact", "effort", "value", "cost"]):
        score += 25

    if any(word in output_lower for word in ["recommend", "should", "priority", "first", "highest"]):
        score += 25

    return score


def score_requirements_doc(output: str) -> float:
    """
    Score requirements documentation quality.

    Criteria:
    - Has clear objective - 20 points
    - Functional requirements listed - 20 points
    - Non-functional requirements - 20 points
    - Success metrics defined - 20 points
    - Well structured/organized - 20 points
    """
    score = 0.0
    output_lower = output.lower()

    if any(word in output_lower for word in ["objective", "goal", "purpose", "overview"]):
        score += 20

    if "functional" in output_lower or "features" in output_lower:
        score += 20

    if "non-functional" in output_lower or any(word in output_lower for word in ["performance", "security", "scalability"]):
        score += 20

    if any(word in output_lower for word in ["metrics", "kpi", "measure", "success criteria"]):
        score += 20

    # Check structure (headings, sections)
    if output.count("#") >= 3 or output.count("\n\n") >= 3:
        score += 20

    return score


def create_product_manager_test_suite() -> TestSuite:
    """Create comprehensive test suite for Product Manager agent."""

    suite = TestSuite(
        name="Product Manager Agent Tests",
        agent_type="product-manager",
        metadata={"version": "1.0", "created": "2025-01-19"}
    )

    # Test 1: User Story Creation
    suite.add_test(TestCase(
        name="Create User Stories for Login Feature",
        task="""Create 3 user stories for a login feature that includes:
        - Email/password login
        - Social login (Google, GitHub)
        - Password reset

        Include acceptance criteria and priorities.""",
        success_criteria=score_user_stories,
        metadata={"difficulty": "medium", "category": "user_stories"}
    ))

    # Test 2: Feature Prioritization
    suite.add_test(TestCase(
        name="Prioritize Features for MVP",
        task="""We have these features proposed for an MVP:
        1. User authentication
        2. Real-time notifications
        3. Advanced analytics dashboard
        4. API rate limiting
        5. Multi-language support

        Prioritize these using RICE framework and explain your reasoning.""",
        success_criteria=score_feature_prioritization,
        metadata={"difficulty": "hard", "category": "prioritization"}
    ))

    # Test 3: Requirements Documentation
    suite.add_test(TestCase(
        name="Document Requirements for Payment System",
        task="""Create a requirements document for integrating a payment system.
        Include functional requirements, non-functional requirements, and success metrics.""",
        success_criteria=score_requirements_doc,
        metadata={"difficulty": "medium", "category": "documentation"}
    ))

    # Test 4: Product Roadmap
    suite.add_test(TestCase(
        name="Create Quarterly Roadmap",
        task="""Create a Q1 product roadmap for a SaaS project management tool.
        Include themes, major features, and timeline.""",
        success_criteria=lambda out: min(100, len(out) / 5),  # Basic length check
        metadata={"difficulty": "medium", "category": "roadmap"}
    ))

    # Test 5: Stakeholder Communication
    suite.add_test(TestCase(
        name="Write Stakeholder Update",
        task="""Write an update email to stakeholders about a feature delay.
        The delay is due to technical complexity. Maintain positive tone while being honest.""",
        success_criteria=lambda out:
            (50 if len(out) > 100 else 0) +
            (25 if "technical" in out.lower() else 0) +
            (25 if any(w in out.lower() for w in ["progress", "working", "timeline"]) else 0),
        metadata={"difficulty": "easy", "category": "communication"}
    ))

    return suite


# Create and export the test suite
product_manager_suite = create_product_manager_test_suite()
