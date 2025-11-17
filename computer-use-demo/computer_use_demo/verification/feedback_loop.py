"""
Feedback Loop - Implements Agent SDK's gather → act → verify → repeat pattern.

Coordinates between:
- Action execution (computer tool, bash, edit)
- Visual verification (screenshot analysis)
- Structural verification (system checks)
- Error recovery and retry logic
"""

import asyncio
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable

from .screenshot_analyzer import ScreenshotAnalyzer, VisualVerification
from .structural_checker import StructuralChecker, StructuralCheck


class ActionType(Enum):
    """Types of actions that can be verified"""
    GUI_INTERACTION = "gui_interaction"
    COMMAND_EXECUTION = "command_execution"
    FILE_OPERATION = "file_operation"
    APPLICATION_LAUNCH = "application_launch"


@dataclass
class Action:
    """An action to be executed and verified"""
    action_type: ActionType
    description: str
    verification_criteria: dict[str, Any]
    retry_on_failure: bool = True
    max_retries: int = 3


@dataclass
class ActionResult:
    """Result of an action execution with verification"""
    action: Action
    success: bool
    visual_verification: VisualVerification | None = None
    structural_checks: list[StructuralCheck] | None = None
    retries_attempted: int = 0
    error: str | None = None


class FeedbackLoop:
    """
    Implements the Agent SDK feedback loop pattern.

    Pattern:
    1. GATHER: Understand current state and requirements
    2. ACT: Execute action via appropriate tool
    3. VERIFY: Check results visually and structurally
    4. REPEAT: Retry if needed or proceed to next action
    """

    def __init__(
        self,
        enable_visual_verification: bool = True,
        enable_structural_verification: bool = True,
        auto_retry: bool = True,
    ):
        """
        Initialize feedback loop.

        Args:
            enable_visual_verification: Whether to use screenshot analysis
            enable_structural_verification: Whether to use structural checks
            auto_retry: Whether to automatically retry failed actions
        """
        self.enable_visual = enable_visual_verification
        self.enable_structural = enable_structural_verification
        self.auto_retry = auto_retry

        self.screenshot_analyzer = ScreenshotAnalyzer()
        self.structural_checker = StructuralChecker()

        self.action_history: list[ActionResult] = []

    async def execute_with_verification(
        self,
        action: Action,
        executor_callback: Callable[[], Any],
        screenshot_callback: Callable[[], str] | None = None,
    ) -> ActionResult:
        """
        Execute an action with full verification feedback loop.

        Args:
            action: Action to execute
            executor_callback: Async function that executes the action
            screenshot_callback: Optional function to capture screenshot

        Returns:
            ActionResult with verification details
        """
        retries = 0
        last_error = None

        while retries <= action.max_retries:
            try:
                # GATHER: Capture state before action (if visual verification enabled)
                before_screenshot = None
                if self.enable_visual and screenshot_callback:
                    try:
                        before_screenshot = await screenshot_callback()
                    except Exception:
                        pass  # Screenshot optional

                # ACT: Execute the action
                await executor_callback()

                # VERIFY: Check results
                visual_verification = None
                structural_checks = []

                # Visual verification
                if self.enable_visual and screenshot_callback:
                    try:
                        after_screenshot = await screenshot_callback()
                        visual_verification = await self.screenshot_analyzer.analyze_screenshot(
                            after_screenshot,
                            expected_state=action.verification_criteria.get("expected_visual_state"),
                            action_taken=action.description,
                        )
                    except Exception as e:
                        visual_verification = VisualVerification(
                            success=False,
                            confidence=0.0,
                            findings=[f"Screenshot capture failed: {e}"],
                        )

                # Structural verification
                if self.enable_structural:
                    structural_checks = await self._run_structural_checks(
                        action.verification_criteria
                    )

                # Determine overall success
                visual_success = (
                    visual_verification.success
                    if visual_verification
                    else True
                )
                structural_success = all(c.success for c in structural_checks) if structural_checks else True

                overall_success = visual_success and structural_success

                # Build result
                result = ActionResult(
                    action=action,
                    success=overall_success,
                    visual_verification=visual_verification,
                    structural_checks=structural_checks,
                    retries_attempted=retries,
                )

                self.action_history.append(result)

                # REPEAT: If failed and retries enabled, try again
                if not overall_success and self.auto_retry and action.retry_on_failure and retries < action.max_retries:
                    retries += 1
                    await asyncio.sleep(2)  # Brief delay before retry
                    continue

                return result

            except Exception as e:
                last_error = str(e)
                retries += 1

                if retries > action.max_retries:
                    break

                await asyncio.sleep(2)

        # All retries exhausted
        result = ActionResult(
            action=action,
            success=False,
            retries_attempted=retries,
            error=last_error or "Maximum retries exceeded",
        )
        self.action_history.append(result)
        return result

    async def _run_structural_checks(
        self,
        verification_criteria: dict[str, Any],
    ) -> list[StructuralCheck]:
        """
        Run structural checks based on verification criteria.

        Args:
            verification_criteria: Dictionary with check specifications

        Returns:
            List of structural check results
        """
        checks = []

        # File existence checks
        if "files_should_exist" in verification_criteria:
            for file_path in verification_criteria["files_should_exist"]:
                check = await self.structural_checker.check_file_exists(file_path)
                checks.append(check)

        # Process checks
        if "processes_should_run" in verification_criteria:
            for process_name in verification_criteria["processes_should_run"]:
                check = await self.structural_checker.check_process_running(process_name)
                checks.append(check)

        # Command output checks
        if "command_checks" in verification_criteria:
            for cmd_check in verification_criteria["command_checks"]:
                check = await self.structural_checker.check_command_output(
                    command=cmd_check["command"],
                    expected_output=cmd_check.get("expected_output"),
                    expected_exit_code=cmd_check.get("expected_exit_code", 0),
                )
                checks.append(check)

        # Port listening checks
        if "ports_should_listen" in verification_criteria:
            for port_spec in verification_criteria["ports_should_listen"]:
                if isinstance(port_spec, int):
                    check = await self.structural_checker.check_port_listening(port_spec)
                else:
                    check = await self.structural_checker.check_port_listening(
                        port_spec["port"],
                        port_spec.get("host", "localhost"),
                    )
                checks.append(check)

        # Directory contents checks
        if "directory_should_contain" in verification_criteria:
            for dir_spec in verification_criteria["directory_should_contain"]:
                check = await self.structural_checker.check_directory_contains(
                    directory=dir_spec["directory"],
                    expected_files=dir_spec["files"],
                )
                checks.append(check)

        return checks

    def create_verification_report(self) -> str:
        """
        Create a human-readable verification report.

        Returns:
            Formatted report string
        """
        if not self.action_history:
            return "No actions executed yet."

        report_lines = ["# Verification Report\n"]

        total_actions = len(self.action_history)
        successful_actions = sum(1 for r in self.action_history if r.success)

        report_lines.append(f"**Total Actions:** {total_actions}")
        report_lines.append(f"**Successful:** {successful_actions}")
        report_lines.append(f"**Failed:** {total_actions - successful_actions}\n")

        for i, result in enumerate(self.action_history, 1):
            status = "✓" if result.success else "✗"
            report_lines.append(f"\n## Action {i}: {status} {result.action.description}")

            if result.retries_attempted > 0:
                report_lines.append(f"*Retries: {result.retries_attempted}*")

            if result.visual_verification:
                report_lines.append(f"\n**Visual Verification:**")
                report_lines.append(f"- Success: {result.visual_verification.success}")
                report_lines.append(f"- Confidence: {result.visual_verification.confidence:.2f}")
                for finding in result.visual_verification.findings:
                    report_lines.append(f"  - {finding}")

            if result.structural_checks:
                report_lines.append(f"\n**Structural Checks:**")
                for check in result.structural_checks:
                    check_status = "✓" if check.success else "✗"
                    report_lines.append(f"- {check_status} {check.check_type}")
                    if check.error:
                        report_lines.append(f"  Error: {check.error}")

            if result.error:
                report_lines.append(f"\n**Error:** {result.error}")

        return "\n".join(report_lines)

    def get_feedback_stats(self) -> dict[str, Any]:
        """
        Get statistics about feedback loop performance.

        Returns:
            Dictionary with feedback loop stats
        """
        total = len(self.action_history)
        successful = sum(1 for r in self.action_history if r.success)
        total_retries = sum(r.retries_attempted for r in self.action_history)

        return {
            "total_actions": total,
            "successful_actions": successful,
            "failed_actions": total - successful,
            "total_retries": total_retries,
            "average_retries": total_retries / total if total > 0 else 0,
            "visual_verifications": sum(
                1 for r in self.action_history if r.visual_verification
            ),
            "structural_checks_performed": sum(
                len(r.structural_checks) if r.structural_checks else 0
                for r in self.action_history
            ),
            "screenshot_analyzer_stats": self.screenshot_analyzer.get_verification_stats(),
            "structural_checker_stats": self.structural_checker.get_check_stats(),
        }
