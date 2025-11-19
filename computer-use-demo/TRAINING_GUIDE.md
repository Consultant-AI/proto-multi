# Agent Training Guide

Guide for running baseline training and improving agent performance.

## Overview

The Proto multi-agent system includes a comprehensive training infrastructure that allows you to:
1. Test agents with standardized scenarios
2. Measure performance objectively (0-100 scores)
3. Track improvement over time
4. Identify areas for enhancement

## Quick Start

### Running Your First Training

```python
import asyncio
from computer_use_demo.agents import ProductManagerAgent
from computer_use_demo.training import TrainingHarness
from computer_use_demo.training.test_suites import product_manager_suite

async def train_pm_agent():
    # Create training harness
    harness = TrainingHarness()

    # Run training
    report = await harness.train_agent(
        agent_class=ProductManagerAgent,
        test_suite=product_manager_suite,
        save_results=True
    )

    # Print summary
    summary = report['summary']
    print(f"\n=== Training Results ===")
    print(f"Total tests: {summary['total']}")
    print(f"Passed: {summary['passed']}")
    print(f"Failed: {summary['failed']}")
    print(f"Pass rate: {summary['pass_rate']:.1f}%")
    print(f"Average score: {summary['average_score']:.1f}/100")
    print(f"Total time: {summary['total_time']:.1f}s")

    # Print individual results
    print(f"\n=== Individual Test Results ===")
    for result in report['results']:
        status = "✓" if result['status'] == 'passed' else "✗"
        print(f"{status} {result['test_name']}: {result['score']:.1f}/100")

# Run training
asyncio.run(train_pm_agent())
```

## Training Workflow

### Phase 1: Baseline Training

Run initial training for each agent to establish baseline performance:

```python
from computer_use_demo.agents import (
    ProductManagerAgent,
    SeniorDeveloperAgent,
    QATestingAgent,
    # ... import all agents
)

agents_to_train = [
    (ProductManagerAgent, product_manager_suite),
    (SeniorDeveloperAgent, developer_suite),
    (QATestingAgent, qa_suite),
    # ... add all agents with their suites
]

async def baseline_training():
    harness = TrainingHarness()

    for agent_class, test_suite in agents_to_train:
        print(f"\n{'='*60}")
        print(f"Training {test_suite.agent_type}")
        print(f"{'='*60}")

        report = await harness.train_agent(
            agent_class=agent_class,
            test_suite=test_suite,
            save_results=True
        )

        print(f"Pass rate: {report['summary']['pass_rate']:.1f}%")
        print(f"Avg score: {report['summary']['average_score']:.1f}")

asyncio.run(baseline_training())
```

### Phase 2: Analyze Results

Review training reports to identify improvement opportunities:

```python
from computer_use_demo.training import TrainingHarness

harness = TrainingHarness()

# Load latest report for an agent
report = harness.load_latest_report("product-manager")

if report:
    # Find failing tests
    for result in report['results']:
        if result['status'] == 'failed':
            print(f"\nFailing test: {result['test_name']}")
            print(f"Score: {result['score']:.1f}")
            print(f"Error: {result['error_message']}")

    # View agent output for analysis
    for result in report['results']:
        if result['score'] < 70:
            print(f"\n=== Low Score: {result['test_name']} ===")
            print(result['agent_output'][:500])
```

### Phase 3: Track Progress

Compare multiple training runs to measure improvement:

```python
comparison = harness.compare_reports("product-manager", limit=5)

if comparison:
    print(f"\n=== Progress for {comparison['agent_type']} ===")
    print(f"Reports analyzed: {comparison['reports_count']}")

    for entry in comparison['history']:
        print(f"\n{entry['timestamp']}")
        print(f"  Pass rate: {entry['pass_rate']:.1f}%")
        print(f"  Avg score: {entry['average_score']:.1f}")

    if 'improvement' in comparison:
        imp = comparison['improvement']
        print(f"\n=== Improvement ===")
        print(f"Pass rate: {imp['pass_rate_delta']:+.1f}%")
        print(f"Avg score: {imp['score_delta']:+.1f}")
```

### Phase 4: Generate Summary

View overall system performance:

```python
summary = harness.generate_summary_report()

print(f"\n=== Multi-Agent System Summary ===")
print(f"Total agents: {summary['total_agents']}")
print(f"Total training runs: {summary['total_reports']}")

print(f"\n=== Agent Performance ===")
for agent in summary['agents']:
    print(f"\n{agent['agent_type']}:")
    print(f"  Runs: {agent['total_runs']}")
    print(f"  Latest pass rate: {agent['latest_pass_rate']:.1f}%")
    print(f"  Latest score: {agent['latest_score']:.1f}")
    print(f"  Best pass rate: {agent['best_pass_rate']:.1f}%")
    print(f"  Best score: {agent['best_score']:.1f}")
```

## Training Results Storage

Training reports are automatically saved to `.proto/training/`:

```
.proto/training/
├── product-manager_20250119_143022.json
├── senior-developer_20250119_143145.json
├── qa-testing_20250119_143309.json
└── ...
```

Each report contains:
- Agent type and test suite name
- Timestamp and duration
- Summary statistics (pass rate, avg score, total tests)
- Individual test results with scores and outputs
- Metadata (test suite version, etc.)

## Interpreting Results

### Score Ranges

- **90-100**: Excellent - Agent exceeds expectations
- **70-89**: Good - Agent meets requirements (passing)
- **50-69**: Fair - Partial success (failing)
- **0-49**: Poor - Significant improvements needed

### Pass Rate Targets

- **>= 80%**: Production ready for this capability
- **60-79%**: Needs improvement but usable
- **< 60%**: Significant training/refinement needed

### What to Look For

**Green Flags** (Good performance):
- High pass rates (>80%)
- Consistent scores across similar tests
- Quick execution times
- Complete, well-structured outputs

**Red Flags** (Needs work):
- Low pass rates (<60%)
- Inconsistent performance
- Timeout failures
- Incomplete or poorly formatted outputs

## Improving Agent Performance

### 1. Analyze Failing Tests

Review agent outputs for failing tests:
- What did the agent miss?
- Was the task ambiguous?
- Does the agent need better prompts?

### 2. Refine Test Cases

Sometimes tests need adjustment:
- Make tasks more specific
- Adjust scoring criteria
- Add examples in task description

### 3. Enhance Agent Prompts

Update agent system prompts in their class files:
- Add more specific expertise descriptions
- Include formatting guidelines
- Add example outputs

### 4. Iterate and Re-test

After making improvements:
1. Re-run training
2. Compare with baseline
3. Track improvement trends
4. Repeat until targets met

## Batch Training Script

Example script to train all agents:

```python
#!/usr/bin/env python3
"""Train all specialist agents and generate summary report."""

import asyncio
from computer_use_demo.training import TrainingHarness
from computer_use_demo.agents import (
    ProductManagerAgent,
    QATestingAgent,
    DevOpsAgent,
    TechnicalWriterAgent,
    DataAnalystAgent,
    CustomerSuccessAgent,
    SalesAgent,
    MarketingStrategyAgent,
    SeniorDeveloperAgent,
    UXDesignerAgent,
    # Add extended agents...
)

async def train_all_agents():
    """Run training for all agents."""
    harness = TrainingHarness()

    # Define agent/suite pairs
    # TODO: Create test suites for all agents
    agents = [
        (ProductManagerAgent, "product-manager", product_manager_suite),
        # Add more agents...
    ]

    results = []
    for agent_class, agent_type, test_suite in agents:
        print(f"\n{'='*70}")
        print(f"Training: {agent_type}")
        print(f"{'='*70}")

        try:
            report = await harness.train_agent(
                agent_class=agent_class,
                test_suite=test_suite,
                save_results=True
            )
            results.append(report)

            summary = report['summary']
            print(f"✓ Complete - Pass rate: {summary['pass_rate']:.1f}%, "
                  f"Avg score: {summary['average_score']:.1f}")
        except Exception as e:
            print(f"✗ Failed: {e}")

    # Generate overall summary
    print(f"\n{'='*70}")
    print("OVERALL SUMMARY")
    print(f"{'='*70}")

    total_tests = sum(r['summary']['total'] for r in results)
    total_passed = sum(r['summary']['passed'] for r in results)
    avg_pass_rate = sum(r['summary']['pass_rate'] for r in results) / len(results)
    avg_score = sum(r['summary']['average_score'] for r in results) / len(results)

    print(f"Agents trained: {len(results)}")
    print(f"Total tests run: {total_tests}")
    print(f"Total passed: {total_passed}")
    print(f"Overall pass rate: {avg_pass_rate:.1f}%")
    print(f"Overall avg score: {avg_score:.1f}")

if __name__ == "__main__":
    asyncio.run(train_all_agents())
```

## Best Practices

1. **Start Small**: Train one agent first to understand the process
2. **Save Results**: Always save results for tracking progress
3. **Regular Training**: Re-train agents after making changes
4. **Track Trends**: Use comparison reports to monitor improvement
5. **Document Insights**: Note what works and what doesn't
6. **Iterate**: Training is continuous - keep refining

## Next Steps

1. Create test suites for remaining agents (18 more needed)
2. Run baseline training for all agents
3. Document baseline performance
4. Set improvement targets
5. Iterate on low-performing agents
6. Track progress weekly/monthly

## Troubleshooting

**Tests timing out?**
- Increase timeout in TestCase definition
- Simplify task complexity
- Check agent is responding

**Low scores across the board?**
- Review scoring functions (might be too strict)
- Check agent system prompts
- Ensure test tasks are clear

**Inconsistent results?**
- Add more test cases for better coverage
- Check for task ambiguity
- Consider agent temperature setting

---

For more details, see:
- [MULTI_AGENT_SYSTEM.md](MULTI_AGENT_SYSTEM.md) - System overview
- [test_suites/README.md](computer_use_demo/training/test_suites/README.md) - Creating test suites
- [example_test_suite.py](computer_use_demo/training/test_suites/example_test_suite.py) - Working example
