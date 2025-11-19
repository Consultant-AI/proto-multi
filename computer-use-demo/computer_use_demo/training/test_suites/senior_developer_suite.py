"""
Test Suite for Senior Developer Agent.

This module contains test cases for evaluating the Senior Developer specialist agent's
ability to write code, review code, design systems, debug issues, and provide technical guidance.
"""

from computer_use_demo.training import TestCase, TestSuite


def score_code_implementation(output: str) -> float:
    """Score code implementation quality."""
    score = 0.0
    output_lower = output.lower()

    # Code presence (20 points)
    code_indicators = ["function", "class", "def ", "const ", "let ", "var ", "async", "=>"]
    if any(indicator in output_lower for indicator in code_indicators):
        score += 20

    # Error handling (15 points)
    if "try" in output_lower or "catch" in output_lower or "except" in output_lower:
        score += 10
    if "error" in output_lower or "throw" in output_lower or "raise" in output_lower:
        score += 5

    # Input validation (15 points)
    validation_terms = ["validate", "check", "if ", "null", "undefined", "none", "empty"]
    found_validation = sum(1 for term in validation_terms if term in output_lower)
    score += min(15, found_validation * 3)

    # Code organization (15 points)
    if "function" in output_lower or "def " in output_lower:
        # Count functions
        func_count = output_lower.count("function") + output_lower.count("def ")
        score += min(10, func_count * 2.5)
    if "class" in output_lower:
        score += 5

    # Documentation (15 points)
    if "/**" in output or '"""' in output or "///" in output or "#" in output:
        score += 10
    if "@param" in output_lower or "@return" in output_lower or "args:" in output_lower:
        score += 5

    # Best practices (10 points)
    if "const" in output_lower or "readonly" in output_lower or "final" in output_lower:
        score += 5
    if "await" in output_lower or "promise" in output_lower or "async" in output_lower:
        score += 5

    # Testing consideration (10 points)
    if "test" in output_lower or "mock" in output_lower or "testable" in output_lower:
        score += 10

    return min(100, score)


def score_code_review(output: str) -> float:
    """Score code review quality."""
    score = 0.0
    output_lower = output.lower()

    # Issues identified (30 points)
    issue_types = [
        "bug",
        "error",
        "issue",
        "problem",
        "vulnerability",
        "security",
        "performance",
        "memory leak",
    ]
    found_issues = sum(1 for issue in issue_types if issue in output_lower)
    score += min(30, found_issues * 7.5)

    # Specific feedback (25 points)
    if "line" in output_lower or ":" in output:  # Line references
        score += 10
    if "should" in output_lower or "could" in output_lower or "recommend" in output_lower:
        score += 10
    if "example" in output_lower or "instead" in output_lower:
        score += 5

    # Code quality aspects (20 points)
    quality_aspects = ["readability", "maintainability", "complexity", "duplication", "naming"]
    found_aspects = sum(1 for aspect in quality_aspects if aspect in output_lower)
    score += min(20, found_aspects * 5)

    # Security concerns (15 points)
    security_terms = ["sql injection", "xss", "csrf", "authentication", "authorization", "sanitize"]
    found_security = sum(1 for term in security_terms if term in output_lower)
    score += min(15, found_security * 5)

    # Actionable suggestions (10 points)
    if "refactor" in output_lower or "extract" in output_lower or "rename" in output_lower:
        score += 5
    if "add" in output_lower or "remove" in output_lower or "change" in output_lower:
        score += 5

    return min(100, score)


def score_system_design(output: str) -> float:
    """Score system design quality."""
    score = 0.0
    output_lower = output.lower()

    # Architecture components (25 points)
    components = [
        "api",
        "database",
        "cache",
        "queue",
        "load balancer",
        "cdn",
        "storage",
        "microservice",
    ]
    found_components = sum(1 for comp in components if comp in output_lower)
    score += min(25, found_components * 4)

    # Scalability (20 points)
    if "scale" in output_lower or "horizontal" in output_lower or "vertical" in output_lower:
        score += 10
    if "sharding" in output_lower or "partition" in output_lower or "replication" in output_lower:
        score += 10

    # Data flow (15 points)
    if "flow" in output_lower or "request" in output_lower or "response" in output_lower:
        score += 7.5
    if "diagram" in output_lower or "--->" in output or "->" in output:
        score += 7.5

    # Technology choices (15 points)
    tech_mentioned = [
        "postgres",
        "redis",
        "kafka",
        "rabbitmq",
        "elasticsearch",
        "mongodb",
        "nginx",
    ]
    if any(tech in output_lower for tech in tech_mentioned):
        score += 10
    if "because" in output_lower or "rationale" in output_lower or "reason" in output_lower:
        score += 5

    # Trade-offs (10 points)
    if "trade-off" in output_lower or "tradeoff" in output_lower or "vs" in output_lower:
        score += 5
    if "advantage" in output_lower or "disadvantage" in output_lower or "pro" in output_lower:
        score += 5

    # Non-functional requirements (10 points)
    nfr_terms = ["performance", "security", "reliability", "availability", "consistency"]
    found_nfr = sum(1 for term in nfr_terms if term in output_lower)
    score += min(10, found_nfr * 2.5)

    # Error handling (5 points)
    if "error" in output_lower or "failure" in output_lower or "retry" in output_lower:
        score += 5

    return min(100, score)


def score_debugging_approach(output: str) -> float:
    """Score debugging approach."""
    score = 0.0
    output_lower = output.lower()

    # Hypothesis formation (25 points)
    if "hypothesis" in output_lower or "likely" in output_lower or "probably" in output_lower:
        score += 15
    if "because" in output_lower or "root cause" in output_lower:
        score += 10

    # Investigation steps (30 points)
    investigation_terms = ["check", "inspect", "examine", "look at", "verify", "test"]
    found_investigation = sum(1 for term in investigation_terms if term in output_lower)
    score += min(30, found_investigation * 6)

    # Debugging tools (15 points)
    tools = ["log", "debugger", "breakpoint", "console", "profiler", "trace"]
    found_tools = sum(1 for tool in tools if tool in output_lower)
    score += min(15, found_tools * 5)

    # Systematic approach (15 points)
    if "step" in output_lower or "first" in output_lower or "then" in output_lower:
        score += 10
    if "reproduce" in output_lower or "replicate" in output_lower:
        score += 5

    # Solution proposal (10 points)
    if "fix" in output_lower or "solution" in output_lower or "resolve" in output_lower:
        score += 5
    if "prevent" in output_lower or "future" in output_lower:
        score += 5

    # Evidence-based (5 points)
    if "evidence" in output_lower or "indicate" in output_lower or "suggest" in output_lower:
        score += 5

    return min(100, score)


def score_technical_guidance(output: str) -> float:
    """Score technical guidance quality."""
    score = 0.0
    output_lower = output.lower()

    # Clear explanation (25 points)
    if len(output) > 300:  # Sufficient detail
        score += 15
    if "example" in output_lower or "for instance" in output_lower or "e.g." in output_lower:
        score += 10

    # Best practices (20 points)
    practice_terms = ["best practice", "recommended", "should", "pattern", "principle"]
    found_practices = sum(1 for term in practice_terms if term in output_lower)
    score += min(20, found_practices * 5)

    # Reasoning (20 points)
    if "because" in output_lower or "reason" in output_lower or "why" in output_lower:
        score += 10
    if "benefit" in output_lower or "advantage" in output_lower or "improve" in output_lower:
        score += 10

    # Alternatives (15 points)
    if "alternative" in output_lower or "option" in output_lower or "approach" in output_lower:
        score += 10
    if "however" in output_lower or "alternatively" in output_lower:
        score += 5

    # Actionable advice (10 points)
    if "start" in output_lower or "first" in output_lower or "begin" in output_lower:
        score += 5
    if "avoid" in output_lower or "don't" in output_lower or "do not" in output_lower:
        score += 5

    # Resources or references (10 points)
    if "document" in output_lower or "read" in output_lower or "reference" in output_lower:
        score += 5
    if "learn" in output_lower or "understand" in output_lower:
        score += 5

    return min(100, score)


def create_senior_developer_test_suite() -> TestSuite:
    """Create comprehensive test suite for Senior Developer agent."""
    suite = TestSuite(
        name="Senior Developer Agent Tests",
        agent_type="senior-developer",
        metadata={"version": "1.0", "created": "2025-01-19"},
    )

    # Test 1: Code implementation
    suite.add_test(
        TestCase(
            name="Implement Rate Limiting Middleware",
            task="""Implement a rate limiting middleware in JavaScript/TypeScript that:
        - Limits requests to 100 per minute per IP address
        - Returns 429 status code when limit is exceeded
        - Uses Redis for distributed rate limiting
        - Includes proper error handling
        - Works with Express.js

        Write production-ready code with comments and error handling.""",
            success_criteria=score_code_implementation,
            metadata={"difficulty": "medium", "category": "implementation"},
        )
    )

    # Test 2: Code review
    suite.add_test(
        TestCase(
            name="Review Authentication Code",
            task="""Review this authentication code and provide feedback:

```javascript
app.post('/login', (req, res) => {
  const query = "SELECT * FROM users WHERE email = '" + req.body.email + "' AND password = '" + req.body.password + "'";
  db.query(query, (err, results) => {
    if (results.length > 0) {
      req.session.user = results[0];
      res.send({success: true});
    } else {
      res.send({success: false});
    }
  });
});
```

Identify security issues, bugs, and best practice violations. Provide specific
improvements and explain why they're important.""",
            success_criteria=score_code_review,
            metadata={"difficulty": "easy", "category": "code_review"},
        )
    )

    # Test 3: System design
    suite.add_test(
        TestCase(
            name="Design Real-time Notification System",
            task="""Design a scalable real-time notification system that:
        - Supports 1 million concurrent users
        - Delivers notifications via WebSocket, push notifications, and email
        - Handles user preferences (notification types, channels, frequency)
        - Ensures delivery reliability
        - Supports notification history and read status

        Describe the architecture, technology choices, data flow, and scalability approach.
        Consider trade-offs and potential failure scenarios.""",
            success_criteria=score_system_design,
            metadata={"difficulty": "hard", "category": "system_design"},
        )
    )

    # Test 4: Debugging
    suite.add_test(
        TestCase(
            name="Debug Memory Leak Issue",
            task="""A Node.js API server's memory usage grows steadily and eventually crashes after 24-48 hours.
        The application:
        - Handles HTTP requests with Express
        - Connects to PostgreSQL database
        - Uses Redis for caching
        - Processes background jobs with Bull queue
        - Memory starts at 200MB and grows to 2GB+ before crashing

        Provide a systematic debugging approach to identify and fix the memory leak.
        What would you check? What tools would you use? What are the likely causes?""",
            success_criteria=score_debugging_approach,
            metadata={"difficulty": "hard", "category": "debugging"},
        )
    )

    # Test 5: Technical guidance
    suite.add_test(
        TestCase(
            name="Guide Junior Developer on API Design",
            task="""A junior developer asks: "What's the best way to design a RESTful API for our e-commerce
        product catalog? We need to support searching, filtering, pagination, and sorting."

        Provide comprehensive technical guidance covering:
        - REST API design principles
        - Endpoint structure and naming
        - Query parameter conventions
        - Response format
        - Error handling
        - Performance considerations

        Explain your recommendations with examples and reasoning.""",
            success_criteria=score_technical_guidance,
            metadata={"difficulty": "medium", "category": "guidance"},
        )
    )

    return suite


# Export the test suite
senior_developer_suite = create_senior_developer_test_suite()
