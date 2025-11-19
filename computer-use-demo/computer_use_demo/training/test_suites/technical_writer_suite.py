"""
Test Suite for Technical Writer Agent.

This module contains test cases for evaluating the Technical Writer specialist agent's
ability to create documentation, API docs, user guides, tutorials, and technical content.
"""

from computer_use_demo.training import TestCase, TestSuite


def score_api_documentation(output: str) -> float:
    """Score API documentation quality."""
    score = 0.0
    output_lower = output.lower()

    # Overview/introduction (15 points)
    if "overview" in output_lower or "introduction" in output_lower or "about" in output_lower:
        score += 10
    if "purpose" in output_lower or "use case" in output_lower:
        score += 5

    # Endpoint documentation (25 points)
    if "endpoint" in output_lower or "route" in output_lower or "path" in output_lower:
        score += 10
    if "method" in output_lower or ("get" in output_lower or "post" in output_lower):
        score += 7.5
    if "url" in output_lower or "http" in output_lower:
        score += 7.5

    # Parameters (20 points)
    if "parameter" in output_lower or "params" in output_lower:
        score += 10
    if "required" in output_lower or "optional" in output_lower:
        score += 5
    if "type" in output_lower or "string" in output_lower or "integer" in output_lower:
        score += 5

    # Request/response examples (20 points)
    if "example" in output_lower or "sample" in output_lower:
        score += 10
    if "request" in output_lower and "response" in output_lower:
        score += 10

    # Error handling (10 points)
    if "error" in output_lower or "status code" in output_lower:
        score += 5
    if "400" in output or "404" in output or "500" in output:
        score += 5

    # Authentication (10 points)
    if "auth" in output_lower or "token" in output_lower or "api key" in output_lower:
        score += 10

    return min(100, score)


def score_user_guide(output: str) -> float:
    """Score user guide quality."""
    score = 0.0
    output_lower = output.lower()

    # Introduction (15 points)
    if "introduction" in output_lower or "getting started" in output_lower:
        score += 10
    if "overview" in output_lower or "about" in output_lower:
        score += 5

    # Step-by-step instructions (30 points)
    if "step" in output_lower:
        step_count = output_lower.count("step")
        score += min(15, step_count * 3)
    if any(num in output_lower for num in ["1.", "2.", "3.", "4.", "5."]):
        score += 15

    # Screenshots/visuals (10 points)
    visual_terms = ["screenshot", "image", "diagram", "figure", "illustration"]
    if any(term in output_lower for term in visual_terms):
        score += 10

    # Clear headings (15 points)
    if "#" in output or "##" in output:  # Markdown headings
        score += 10
    if output.count("\n\n") >= 3:  # Well-structured sections
        score += 5

    # Tips/notes (10 points)
    tip_terms = ["tip", "note", "important", "warning", "best practice"]
    found_tips = sum(1 for term in tip_terms if term in output_lower)
    score += min(10, found_tips * 3)

    # Troubleshooting (10 points)
    if "troubleshoot" in output_lower or "common issue" in output_lower or "problem" in output_lower:
        score += 10

    # Next steps (10 points)
    if "next" in output_lower or "see also" in output_lower or "related" in output_lower:
        score += 10

    return min(100, score)


def score_tutorial(output: str) -> float:
    """Score tutorial quality."""
    score = 0.0
    output_lower = output.lower()

    # Learning objectives (15 points)
    if "learn" in output_lower or "objective" in output_lower or "will" in output_lower:
        score += 10
    if "by the end" in output_lower or "you will" in output_lower:
        score += 5

    # Prerequisites (10 points)
    if "prerequisite" in output_lower or "before you begin" in output_lower or "requirements" in output_lower:
        score += 10

    # Step-by-step progression (30 points)
    if "step" in output_lower:
        score += 15
    if any(f"{i}." in output for i in range(1, 6)):
        score += 15

    # Code examples (20 points)
    code_indicators = ["```", "code", "example", "function", "class"]
    found_code = sum(1 for indicator in code_indicators if indicator in output_lower)
    score += min(20, found_code * 5)

    # Explanations (15 points)
    explain_terms = ["this", "because", "why", "how", "what"]
    if sum(1 for term in explain_terms if term in output_lower) >= 3:
        score += 15

    # Practice/exercise (10 points)
    if "try" in output_lower or "exercise" in output_lower or "practice" in output_lower:
        score += 10

    return min(100, score)


def score_release_notes(output: str) -> float:
    """Score release notes quality."""
    score = 0.0
    output_lower = output.lower()

    # Version and date (15 points)
    if "version" in output_lower or "v" in output_lower or "release" in output_lower:
        score += 10
    if "date" in output_lower or "2025" in output or "january" in output_lower:
        score += 5

    # Categorization (25 points)
    categories = ["new feature", "improvement", "bug fix", "breaking change", "deprecated"]
    found_categories = sum(1 for cat in categories if cat in output_lower)
    score += min(25, found_categories * 6.25)

    # Clear descriptions (20 points)
    if len(output) > 300:  # Sufficient detail
        score += 10
    bullet_indicators = ["-", "*", "•"]
    if any(indicator in output for indicator in bullet_indicators):
        score += 10

    # User impact (15 points)
    if "user" in output_lower or "customer" in output_lower:
        score += 7.5
    if "impact" in output_lower or "affect" in output_lower or "change" in output_lower:
        score += 7.5

    # Migration/upgrade info (15 points)
    if "upgrade" in output_lower or "migration" in output_lower or "how to" in output_lower:
        score += 10
    if "action required" in output_lower or "breaking" in output_lower:
        score += 5

    # Links/references (10 points)
    if "see" in output_lower or "documentation" in output_lower or "link" in output_lower:
        score += 10

    return min(100, score)


def score_readme(output: str) -> float:
    """Score README quality."""
    score = 0.0
    output_lower = output.lower()

    # Project description (15 points)
    if len(output) > 100:  # Has content
        score += 10
    if "description" in output_lower or "about" in output_lower or "what" in output_lower:
        score += 5

    # Installation instructions (20 points)
    if "install" in output_lower or "setup" in output_lower:
        score += 15
    if "npm" in output_lower or "pip" in output_lower or "yarn" in output_lower:
        score += 5

    # Usage examples (20 points)
    if "usage" in output_lower or "example" in output_lower or "how to" in output_lower:
        score += 10
    if "```" in output or "code" in output_lower:
        score += 10

    # Features (15 points)
    if "feature" in output_lower or "capability" in output_lower:
        score += 10
    if "-" in output or "*" in output:  # Bullet points
        score += 5

    # Documentation links (10 points)
    if "documentation" in output_lower or "docs" in output_lower:
        score += 5
    if "link" in output_lower or "http" in output_lower or "read more" in output_lower:
        score += 5

    # Contributing/license (10 points)
    if "contribut" in output_lower or "pull request" in output_lower:
        score += 5
    if "license" in output_lower or "mit" in output_lower:
        score += 5

    # Getting started (10 points)
    if "getting started" in output_lower or "quick start" in output_lower:
        score += 10

    return min(100, score)


def create_technical_writer_test_suite() -> TestSuite:
    """Create comprehensive test suite for Technical Writer agent."""
    suite = TestSuite(
        name="Technical Writer Agent Tests",
        agent_type="technical-writer",
        metadata={"version": "1.0", "created": "2025-01-19"},
    )

    # Test 1: API documentation
    suite.add_test(
        TestCase(
            name="Write REST API Documentation",
            task="""Document this REST API endpoint:

POST /api/users
Creates a new user account

Parameters:
- email (string, required): User's email address
- password (string, required): Password (min 8 chars)
- name (string, required): Full name
- role (string, optional): User role (default: "user")

Returns:
- 201: User created successfully
- 400: Invalid input
- 409: Email already exists

Authentication: Requires API key in header

Create comprehensive API documentation including:
- Overview of the endpoint
- Request format and parameters
- Response format and examples
- Error codes and handling
- Authentication requirements""",
            success_criteria=score_api_documentation,
            metadata={"difficulty": "medium", "category": "api_docs"},
        )
    )

    # Test 2: User guide
    suite.add_test(
        TestCase(
            name="Create Feature User Guide",
            task="""Write a user guide for a new "File Sharing" feature that allows users to:
- Upload files to shared folders
- Set permissions (view/edit)
- Share links with expiration dates
- Track who accessed files

Target audience: Non-technical business users

Create a user-friendly guide with:
- Introduction explaining the feature
- Step-by-step instructions for common tasks
- Screenshots or visual references (describe what should be shown)
- Tips and best practices
- Troubleshooting common issues""",
            success_criteria=score_user_guide,
            metadata={"difficulty": "medium", "category": "user_guide"},
        )
    )

    # Test 3: Tutorial
    suite.add_test(
        TestCase(
            name="Write Getting Started Tutorial",
            task="""Create a "Getting Started" tutorial for developers new to your project management API.

The tutorial should teach them how to:
1. Set up authentication
2. Create their first project
3. Add tasks to the project
4. Update task status
5. Retrieve project data

Include:
- Clear learning objectives
- Prerequisites (what they need to know)
- Step-by-step instructions with code examples
- Explanations of what each step does
- A practice exercise at the end

Make it beginner-friendly and hands-on.""",
            success_criteria=score_tutorial,
            metadata={"difficulty": "hard", "category": "tutorial"},
        )
    )

    # Test 4: Release notes
    suite.add_test(
        TestCase(
            name="Write Product Release Notes",
            task="""Write release notes for version 2.5.0 of a SaaS product with these changes:

New Features:
- Advanced search with filters
- Dark mode UI option
- Bulk export to CSV

Improvements:
- Dashboard load time reduced by 40%
- Mobile app now works offline
- Better error messages

Bug Fixes:
- Fixed data sync issue affecting 2% of users
- Resolved login timeout on Safari

Breaking Changes:
- API endpoint /v1/data renamed to /v2/data
- Old endpoint deprecated, will be removed in 3 months

Create professional release notes that:
- Are clearly organized by category
- Explain impact to users
- Include migration instructions for breaking changes
- Have appropriate tone for customers""",
            success_criteria=score_release_notes,
            metadata={"difficulty": "medium", "category": "release_notes"},
        )
    )

    # Test 5: README
    suite.add_test(
        TestCase(
            name="Create Project README",
            task="""Create a README.md for an open-source JavaScript library called "DataViz"
that helps developers create interactive charts and graphs.

Key features:
- Supports 10+ chart types
- Responsive and mobile-friendly
- Easy API (just a few lines of code)
- Customizable themes
- Lightweight (only 15KB)

Include:
- Project description
- Installation instructions
- Quick start / usage example
- List of features
- Link to full documentation
- Contributing guidelines
- License information

Make it engaging and developer-friendly.""",
            success_criteria=score_readme,
            metadata={"difficulty": "easy", "category": "readme"},
        )
    )

    return suite


# Export the test suite
technical_writer_suite = create_technical_writer_test_suite()
