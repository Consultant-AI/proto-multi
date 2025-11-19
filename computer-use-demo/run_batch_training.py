#!/usr/bin/env python3
"""
Batch training script for multiple agents.

This script runs training for multiple agents in sequence and generates
a summary report of all training results.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Load environment variables
from dotenv import load_dotenv

load_dotenv()

# Verify API key is loaded
if not os.getenv("ANTHROPIC_API_KEY"):
    print("Error: ANTHROPIC_API_KEY not found in environment variables")
    print("Please ensure .env file exists with ANTHROPIC_API_KEY set")
    sys.exit(1)

from computer_use_demo.agents import (
    CustomerSuccessAgent,
    DevOpsAgent,
    ProductManagerAgent,
    QATestingAgent,
    SalesAgent,
    SeniorDeveloperAgent,
)
from computer_use_demo.training import TrainingHarness
from computer_use_demo.training.test_suites import (
    customer_success_suite,
    devops_suite,
    product_manager_suite,
    qa_testing_suite,
    sales_suite,
    senior_developer_suite,
)


async def main():
    """Run batch training for multiple agents."""
    print("=" * 80)
    print("BATCH AGENT TRAINING")
    print("=" * 80)
    print()

    # Define agents and their test suites
    agents_to_train = [
        (ProductManagerAgent, product_manager_suite, "Product Manager"),
        (QATestingAgent, qa_testing_suite, "QA Testing"),
        (DevOpsAgent, devops_suite, "DevOps"),
        (SeniorDeveloperAgent, senior_developer_suite, "Senior Developer"),
        (SalesAgent, sales_suite, "Sales"),
        (CustomerSuccessAgent, customer_success_suite, "Customer Success"),
    ]

    # Create training harness
    harness = TrainingHarness()

    # Track overall results
    all_results = []
    total_start_time = asyncio.get_event_loop().time()

    # Train each agent
    for idx, (agent_class, test_suite, agent_name) in enumerate(agents_to_train, 1):
        print(f"\n{'=' * 80}")
        print(f"[{idx}/{len(agents_to_train)}] Training: {agent_name}")
        print(f"Test Suite: {test_suite.name}")
        print(f"Number of Tests: {len(test_suite.test_cases)}")
        print(f"{'=' * 80}\n")

        try:
            # Run training
            report = await harness.train_agent(
                agent_class=agent_class,
                test_suite=test_suite,
                save_results=True,
            )

            # Store results
            all_results.append(
                {
                    "agent_name": agent_name,
                    "agent_type": test_suite.agent_type,
                    "report": report,
                }
            )

            # Print summary
            summary = report["summary"]
            print(f"\n{'─' * 80}")
            print(f"✓ {agent_name} Training Complete")
            print(f"{'─' * 80}")
            print(f"Pass rate: {summary['pass_rate']:.1f}% ({summary['passed']}/{summary['total']})")
            print(f"Average score: {summary['average_score']:.1f}/100")
            print(f"Total time: {summary['total_time']:.1f}s")
            print(f"{'─' * 80}")

        except Exception as e:
            print(f"\n✗ {agent_name} Training Failed")
            print(f"Error: {e}")
            import traceback

            traceback.print_exc()
            all_results.append(
                {
                    "agent_name": agent_name,
                    "agent_type": test_suite.agent_type,
                    "error": str(e),
                }
            )

    total_end_time = asyncio.get_event_loop().time()
    total_duration = total_end_time - total_start_time

    # Print overall summary
    print(f"\n\n{'=' * 80}")
    print("BATCH TRAINING SUMMARY")
    print(f"{'=' * 80}\n")

    successful_trainings = [r for r in all_results if "report" in r]
    failed_trainings = [r for r in all_results if "error" in r]

    print(f"Total agents trained: {len(agents_to_train)}")
    print(f"Successful: {len(successful_trainings)}")
    print(f"Failed: {len(failed_trainings)}")
    print(f"Total duration: {total_duration:.1f}s ({total_duration/60:.1f} minutes)")
    print()

    if successful_trainings:
        print(f"{'─' * 80}")
        print("AGENT PERFORMANCE SUMMARY")
        print(f"{'─' * 80}\n")

        # Calculate overall statistics
        total_tests = sum(r["report"]["summary"]["total"] for r in successful_trainings)
        total_passed = sum(r["report"]["summary"]["passed"] for r in successful_trainings)
        avg_pass_rate = (
            sum(r["report"]["summary"]["pass_rate"] for r in successful_trainings)
            / len(successful_trainings)
        )
        avg_score = (
            sum(r["report"]["summary"]["average_score"] for r in successful_trainings)
            / len(successful_trainings)
        )

        print(f"Overall Statistics:")
        print(f"  Total tests run: {total_tests}")
        print(f"  Total passed: {total_passed}")
        print(f"  Overall pass rate: {avg_pass_rate:.1f}%")
        print(f"  Overall average score: {avg_score:.1f}/100")
        print()

        # Individual agent performance
        print("Individual Agent Performance:")
        print(f"{'─' * 80}")
        print(f"{'Agent':<25} {'Pass Rate':<15} {'Avg Score':<15} {'Tests':<10}")
        print(f"{'─' * 80}")

        for result in successful_trainings:
            summary = result["report"]["summary"]
            print(
                f"{result['agent_name']:<25} "
                f"{summary['pass_rate']:>6.1f}% "
                f"({summary['passed']}/{summary['total']})"
                f"{'':<4} "
                f"{summary['average_score']:>6.1f}/100"
                f"{'':<4} "
                f"{summary['total']:<10}"
            )

        print(f"{'─' * 80}\n")

    if failed_trainings:
        print(f"{'─' * 80}")
        print("FAILED TRAININGS")
        print(f"{'─' * 80}\n")

        for result in failed_trainings:
            print(f"✗ {result['agent_name']}")
            print(f"  Error: {result['error']}\n")

    # Print report locations
    if successful_trainings:
        print(f"{'─' * 80}")
        print("TRAINING REPORTS SAVED")
        print(f"{'─' * 80}\n")

        for result in successful_trainings:
            if "report_path" in result["report"]:
                print(f"  {result['agent_name']}: {result['report']['report_path']}")

        print()

    print(f"{'=' * 80}\n")

    return 0 if not failed_trainings else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
