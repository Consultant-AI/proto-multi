#!/usr/bin/env python3
"""
Run training for Product Manager agent.

This script demonstrates the training system by running the PM agent
through the example test suite.
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

from computer_use_demo.agents import ProductManagerAgent
from computer_use_demo.training import TrainingHarness
from computer_use_demo.training.test_suites import product_manager_suite


async def main():
    """Run PM agent training."""
    print("=" * 70)
    print("Product Manager Agent Training")
    print("=" * 70)
    print()

    # Create training harness
    harness = TrainingHarness()

    # Run training
    print("Running test suite...")
    print(f"Test suite: {product_manager_suite.name}")
    print(f"Number of tests: {len(product_manager_suite.test_cases)}")
    print()

    try:
        report = await harness.train_agent(
            agent_class=ProductManagerAgent,
            test_suite=product_manager_suite,
            save_results=True,
        )

        # Print summary
        summary = report["summary"]
        print()
        print("=" * 70)
        print("TRAINING RESULTS")
        print("=" * 70)
        print(f"Total tests: {summary['total']}")
        print(f"Passed: {summary['passed']}")
        print(f"Failed: {summary['failed']}")
        print(f"Pass rate: {summary['pass_rate']:.1f}%")
        print(f"Average score: {summary['average_score']:.1f}/100")
        print(f"Total time: {summary['total_time']:.1f}s")
        print()

        # Print individual results
        print("=" * 70)
        print("INDIVIDUAL TEST RESULTS")
        print("=" * 70)
        for result in report["results"]:
            status = "✓" if result["status"] == "passed" else "✗"
            print(f"{status} {result['test_name']}")
            print(f"  Score: {result['score']:.1f}/100")
            print(f"  Time: {result['execution_time']:.1f}s")
            if result["error_message"]:
                print(f"  Error: {result['error_message']}")
            print()

        # Show where report was saved
        if "report_path" in report:
            print("=" * 70)
            print(f"Report saved to: {report['report_path']}")
            print("=" * 70)

    except Exception as e:
        print(f"Training failed with error: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
