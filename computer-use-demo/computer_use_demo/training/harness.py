"""
Training Harness for Proto Multi-Agent System.

Provides automated testing and training capabilities for agents.
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Type

from ..agents.base_agent import BaseAgent
from ..proto_logging import get_logger
from .test_case import TestResult, TestStatus, TestSuite


class TrainingHarness:
    """
    Automated training harness for agents.

    Runs test suites, collects results, and generates training reports.
    """

    def __init__(self, results_dir: Path | None = None):
        """
        Initialize training harness.

        Args:
            results_dir: Directory to save training results (default: .proto/training)
        """
        self.logger = get_logger()
        self.results_dir = results_dir or Path(".proto/training")
        self.results_dir.mkdir(parents=True, exist_ok=True)

    async def train_agent(
        self,
        agent_class: Type[BaseAgent],
        test_suite: TestSuite,
        tools: list[Any] | None = None,
        save_results: bool = True,
    ) -> dict[str, Any]:
        """
        Train an agent by running its test suite.

        Args:
            agent_class: The agent class to train
            test_suite: Test suite to run
            tools: Tools to provide to the agent
            save_results: Whether to save results to disk

        Returns:
            Training report with results and statistics
        """
        self.logger.log_event(
            event_type="training_started",
            session_id="training-harness",
            data={
                "agent_type": test_suite.agent_type,
                "test_count": len(test_suite.test_cases),
            },
        )

        # Instantiate agent
        agent = agent_class(tools=tools)

        # Run all tests
        start_time = datetime.now()
        results = await test_suite.run_all(agent)
        end_time = datetime.now()

        # Generate report
        summary = test_suite.get_summary(results)
        report = {
            "agent_type": test_suite.agent_type,
            "suite_name": test_suite.name,
            "timestamp": start_time.isoformat(),
            "duration": (end_time - start_time).total_seconds(),
            "summary": summary,
            "results": [self._result_to_dict(r) for r in results],
            "metadata": test_suite.metadata,
        }

        # Log summary
        self.logger.log_event(
            event_type="training_completed",
            session_id="training-harness",
            data={
                "agent_type": test_suite.agent_type,
                "pass_rate": summary["pass_rate"],
                "average_score": summary["average_score"],
            },
        )

        # Save results if requested
        if save_results:
            self._save_report(report)

        return report

    async def train_multiple_agents(
        self,
        agent_configs: list[dict[str, Any]],
        save_results: bool = True,
    ) -> list[dict[str, Any]]:
        """
        Train multiple agents in parallel.

        Args:
            agent_configs: List of dicts with 'agent_class', 'test_suite', and 'tools'
            save_results: Whether to save results to disk

        Returns:
            List of training reports
        """
        tasks = []
        for config in agent_configs:
            task = self.train_agent(
                agent_class=config["agent_class"],
                test_suite=config["test_suite"],
                tools=config.get("tools"),
                save_results=save_results,
            )
            tasks.append(task)

        reports = await asyncio.gather(*tasks)
        return list(reports)

    def _result_to_dict(self, result: TestResult) -> dict[str, Any]:
        """Convert TestResult to dictionary for JSON serialization."""
        return {
            "test_name": result.test_name,
            "status": result.status.value,
            "score": result.score,
            "execution_time": result.execution_time,
            "agent_output": result.agent_output[:500],  # Truncate for readability
            "error_message": result.error_message,
            "metadata": result.metadata,
        }

    def _save_report(self, report: dict[str, Any]) -> None:
        """Save training report to disk."""
        agent_type = report["agent_type"]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{agent_type}_{timestamp}.json"
        filepath = self.results_dir / filename

        with open(filepath, "w") as f:
            json.dump(report, f, indent=2)

        self.logger.log_event(
            event_type="training_report_saved",
            session_id="training-harness",
            data={"filepath": str(filepath)},
        )

    def load_latest_report(self, agent_type: str) -> dict[str, Any] | None:
        """
        Load the most recent training report for an agent.

        Args:
            agent_type: Type of agent (e.g., "marketing-strategy")

        Returns:
            Training report or None if not found
        """
        pattern = f"{agent_type}_*.json"
        reports = sorted(self.results_dir.glob(pattern), reverse=True)

        if not reports:
            return None

        with open(reports[0]) as f:
            return json.load(f)

    def compare_reports(
        self, agent_type: str, limit: int = 5
    ) -> dict[str, Any] | None:
        """
        Compare recent training reports to show progress.

        Args:
            agent_type: Type of agent
            limit: Number of recent reports to compare

        Returns:
            Comparison data or None if insufficient reports
        """
        pattern = f"{agent_type}_*.json"
        reports = sorted(self.results_dir.glob(pattern), reverse=True)[:limit]

        if len(reports) < 2:
            return None

        comparison = {
            "agent_type": agent_type,
            "reports_count": len(reports),
            "history": [],
        }

        for report_path in reports:
            with open(report_path) as f:
                report = json.load(f)
                comparison["history"].append(
                    {
                        "timestamp": report["timestamp"],
                        "pass_rate": report["summary"]["pass_rate"],
                        "average_score": report["summary"]["average_score"],
                        "total_tests": report["summary"]["total"],
                    }
                )

        # Calculate improvement
        if len(comparison["history"]) >= 2:
            latest = comparison["history"][0]
            previous = comparison["history"][1]
            comparison["improvement"] = {
                "pass_rate_delta": latest["pass_rate"] - previous["pass_rate"],
                "score_delta": latest["average_score"] - previous["average_score"],
            }

        return comparison

    def generate_summary_report(self) -> dict[str, Any]:
        """
        Generate a summary report of all agent training.

        Returns:
            Summary report with statistics for all agents
        """
        all_reports = list(self.results_dir.glob("*.json"))

        if not all_reports:
            return {"agents": [], "total_reports": 0}

        agents_data = {}

        for report_path in all_reports:
            with open(report_path) as f:
                report = json.load(f)
                agent_type = report["agent_type"]

                if agent_type not in agents_data:
                    agents_data[agent_type] = {
                        "agent_type": agent_type,
                        "total_runs": 0,
                        "latest_pass_rate": 0.0,
                        "latest_score": 0.0,
                        "best_pass_rate": 0.0,
                        "best_score": 0.0,
                    }

                data = agents_data[agent_type]
                data["total_runs"] += 1

                pass_rate = report["summary"]["pass_rate"]
                score = report["summary"]["average_score"]

                # Update best scores
                if pass_rate > data["best_pass_rate"]:
                    data["best_pass_rate"] = pass_rate
                if score > data["best_score"]:
                    data["best_score"] = score

                # Update latest (files sorted, so last one is latest)
                data["latest_pass_rate"] = pass_rate
                data["latest_score"] = score

        return {
            "agents": list(agents_data.values()),
            "total_reports": len(all_reports),
            "total_agents": len(agents_data),
        }
