"""
Test Case Infrastructure for Agent Training.

Provides classes for defining, running, and scoring agent test cases.
"""

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable


class TestStatus(Enum):
    """Test execution status."""

    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    ERROR = "error"


@dataclass
class TestResult:
    """
    Result of running a test case.

    Attributes:
        test_name: Name of the test
        status: Test execution status
        score: Quality score (0-100)
        execution_time: Time taken in seconds
        agent_output: The agent's output/response
        error_message: Error message if failed
        metadata: Additional test metadata
    """

    test_name: str
    status: TestStatus
    score: float = 0.0
    execution_time: float = 0.0
    agent_output: str = ""
    error_message: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        """String representation of test result."""
        status_emoji = {
            TestStatus.PASSED: "✓",
            TestStatus.FAILED: "✗",
            TestStatus.ERROR: "⚠",
            TestStatus.PENDING: "○",
            TestStatus.RUNNING: "◐",
        }
        emoji = status_emoji.get(self.status, "?")
        return f"{emoji} {self.test_name}: {self.status.value} (score: {self.score:.1f})"


@dataclass
class TestCase:
    """
    A test case for an agent.

    Attributes:
        name: Test name/identifier
        task: The task prompt to give the agent
        success_criteria: Function to evaluate agent output (returns score 0-100)
        metadata: Additional test metadata (e.g., difficulty, category)
        timeout: Maximum execution time in seconds
    """

    name: str
    task: str
    success_criteria: Callable[[str], float]
    metadata: dict[str, Any] = field(default_factory=dict)
    timeout: int = 300  # 5 minutes default

    async def run(self, agent: Any) -> TestResult:
        """
        Run this test case with the given agent.

        Args:
            agent: The agent to test

        Returns:
            TestResult with execution details and score
        """
        start_time = time.time()
        result = TestResult(test_name=self.name, status=TestStatus.RUNNING)

        try:
            # Execute agent with the task
            agent_result = await agent.execute(self.task, context={})

            execution_time = time.time() - start_time

            if not agent_result.success:
                result.status = TestStatus.FAILED
                result.error_message = agent_result.error
                result.agent_output = agent_result.output
                result.execution_time = execution_time
                result.score = 0.0
                return result

            # Evaluate output using success criteria
            try:
                score = self.success_criteria(agent_result.output)
                score = max(0.0, min(100.0, score))  # Clamp to 0-100
            except Exception as e:
                result.status = TestStatus.ERROR
                result.error_message = f"Scoring failed: {str(e)}"
                result.agent_output = agent_result.output
                result.execution_time = execution_time
                result.score = 0.0
                return result

            # Determine status based on score
            if score >= 70:
                result.status = TestStatus.PASSED
            else:
                result.status = TestStatus.FAILED

            result.score = score
            result.agent_output = agent_result.output
            result.execution_time = execution_time
            result.metadata = {
                **self.metadata,
                "iterations": agent_result.iterations,
            }

            return result

        except Exception as e:
            execution_time = time.time() - start_time
            result.status = TestStatus.ERROR
            result.error_message = f"Execution error: {str(e)}"
            result.execution_time = execution_time
            result.score = 0.0
            return result


@dataclass
class TestSuite:
    """
    A collection of test cases for an agent.

    Attributes:
        name: Suite name (e.g., "MarketingStrategyAgent Tests")
        agent_type: Type of agent being tested
        test_cases: List of test cases in this suite
        metadata: Additional suite metadata
    """

    name: str
    agent_type: str
    test_cases: list[TestCase] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def add_test(self, test_case: TestCase) -> None:
        """Add a test case to this suite."""
        self.test_cases.append(test_case)

    async def run_all(self, agent: Any) -> list[TestResult]:
        """
        Run all test cases in this suite.

        Args:
            agent: The agent to test

        Returns:
            List of test results
        """
        results = []
        for test_case in self.test_cases:
            result = await test_case.run(agent)
            results.append(result)
        return results

    def get_summary(self, results: list[TestResult]) -> dict[str, Any]:
        """
        Get summary statistics for test results.

        Args:
            results: List of test results

        Returns:
            Dictionary with summary statistics
        """
        if not results:
            return {
                "total": 0,
                "passed": 0,
                "failed": 0,
                "errors": 0,
                "average_score": 0.0,
                "pass_rate": 0.0,
            }

        passed = sum(1 for r in results if r.status == TestStatus.PASSED)
        failed = sum(1 for r in results if r.status == TestStatus.FAILED)
        errors = sum(1 for r in results if r.status == TestStatus.ERROR)
        total = len(results)
        average_score = sum(r.score for r in results) / total if total > 0 else 0.0
        pass_rate = (passed / total * 100) if total > 0 else 0.0

        return {
            "total": total,
            "passed": passed,
            "failed": failed,
            "errors": errors,
            "average_score": average_score,
            "pass_rate": pass_rate,
            "total_time": sum(r.execution_time for r in results),
        }
