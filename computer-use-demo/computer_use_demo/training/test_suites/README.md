# Agent Test Suites

This directory contains test suites for training and evaluating specialist agents.

## Structure

Each test suite file defines:
1. **Scoring functions**: Functions that evaluate agent output (return 0-100)
2. **Test cases**: Individual tests with tasks and success criteria
3. **Test suite**: Collection of related test cases for an agent

## Creating a Test Suite

```python
from computer_use_demo.agents import YourAgent
from computer_use_demo.training import TestCase, TestSuite

# 1. Define scoring function
def score_output(output: str) -> float:
    """Score agent output based on quality criteria."""
    score = 0.0
    # Add scoring logic (return 0-100)
    if "keyword" in output.lower():
        score += 50
    if len(output) > 200:
        score += 50
    return score

# 2. Create test suite
suite = TestSuite(
    name="Your Agent Tests",
    agent_type="your-agent-role",
    metadata={"version": "1.0"}
)

# 3. Add test cases
suite.add_test(TestCase(
    name="Test Description",
    task="Detailed task instructions for the agent",
    success_criteria=score_output,
    metadata={"difficulty": "medium"}
))

# 4. Export
your_agent_suite = suite
```

## Scoring Guidelines

### Score Ranges
- **90-100**: Excellent - Exceeds expectations
- **70-89**: Good - Meets all requirements (passing)
- **50-69**: Fair - Partially meets requirements (failing)
- **0-49**: Poor - Does not meet requirements

### Scoring Criteria Examples

**Content Quality**:
- Completeness (has all required elements)
- Accuracy (correct information)
- Structure (well-organized)
- Clarity (easy to understand)

**Task-Specific**:
- For PM: User story format, acceptance criteria, priorities
- For Dev: Code quality, test coverage, documentation
- For QA: Test coverage, edge cases, clear steps
- For Sales: Value proposition, objection handling, next steps

## Running Tests

```python
from computer_use_demo.training import TrainingHarness
from computer_use_demo.agents import ProductManagerAgent
from .example_test_suite import product_manager_suite

# Create harness
harness = TrainingHarness()

# Run training
report = await harness.train_agent(
    agent_class=ProductManagerAgent,
    test_suite=product_manager_suite,
    save_results=True
)

# View results
print(f"Pass rate: {report['summary']['pass_rate']:.1f}%")
print(f"Average score: {report['summary']['average_score']:.1f}")
```

## Test Suite Template

Use `example_test_suite.py` as a template for creating new test suites.

### Recommended Test Count per Agent
- **Minimum**: 5 tests covering core capabilities
- **Standard**: 7-10 tests covering various scenarios
- **Comprehensive**: 15+ tests with edge cases

### Test Categories
- Basic tasks (easy difficulty)
- Standard workflows (medium difficulty)
- Complex scenarios (hard difficulty)
- Edge cases and error handling

## Best Practices

1. **Clear Tasks**: Write specific, unambiguous task descriptions
2. **Objective Scoring**: Use measurable criteria in scoring functions
3. **Incremental Difficulty**: Start easy, progress to complex
4. **Real-World Scenarios**: Base tests on actual use cases
5. **Comprehensive Coverage**: Test all major agent capabilities
6. **Metadata**: Include difficulty, category, and version info

## Example Test Categories by Agent

**Product Manager**:
- User story creation
- Feature prioritization
- Requirements documentation
- Roadmap planning
- Stakeholder communication

**Developer**:
- Code implementation
- Bug fixing
- Code review
- Architecture decisions
- Documentation

**QA Testing**:
- Test case creation
- Bug reporting
- Test automation
- Edge case identification
- Quality metrics

**DevOps**:
- Infrastructure setup
- CI/CD configuration
- Deployment scripts
- Monitoring setup
- Incident response

## Next Steps

1. Create test suites for all 19 specialist agents
2. Run baseline training to establish benchmarks
3. Iterate and improve based on results
4. Track progress over time

---

See `example_test_suite.py` for a complete working example.
