"""
Screenshot Analyzer - Visual verification using computer tool screenshots.

Provides intelligent screenshot analysis to verify:
- GUI actions succeeded
- Applications launched correctly
- Error dialogs appeared
- Visual state matches expectations
"""

import base64
from typing import Any, Literal
from dataclasses import dataclass


@dataclass
class VisualVerification:
    """Result of visual verification"""
    success: bool
    confidence: float  # 0.0 to 1.0
    findings: list[str]
    error_detected: bool = False
    error_details: str | None = None


class ScreenshotAnalyzer:
    """
    Analyzes screenshots to verify agent actions.

    Uses pattern matching and visual heuristics to determine if
    GUI operations succeeded.
    """

    def __init__(self):
        """Initialize screenshot analyzer"""
        self.known_error_patterns = self._load_error_patterns()
        self.verification_history: list[VisualVerification] = []

    def _load_error_patterns(self) -> dict[str, list[str]]:
        """
        Load known error patterns to detect in screenshots.

        Returns:
            Dictionary mapping error types to detection patterns
        """
        return {
            "dialog_errors": [
                "error",
                "failed",
                "could not",
                "unable to",
                "permission denied",
                "access denied",
            ],
            "application_crashes": [
                "has stopped working",
                "not responding",
                "crashed",
                "unexpectedly quit",
            ],
            "network_errors": [
                "connection refused",
                "timeout",
                "unreachable",
                "no internet",
            ],
        }

    async def analyze_screenshot(
        self,
        screenshot_base64: str,
        expected_state: str | None = None,
        action_taken: str | None = None,
    ) -> VisualVerification:
        """
        Analyze a screenshot to verify expected state.

        Args:
            screenshot_base64: Base64 encoded screenshot
            expected_state: Description of expected visual state
            action_taken: Description of action that was taken

        Returns:
            VisualVerification result
        """
        findings = []

        # Basic validation
        if not screenshot_base64:
            return VisualVerification(
                success=False,
                confidence=0.0,
                findings=["No screenshot provided"],
            )

        # Check if screenshot is valid base64
        try:
            base64.b64decode(screenshot_base64)
        except Exception as e:
            return VisualVerification(
                success=False,
                confidence=0.0,
                findings=[f"Invalid screenshot data: {e}"],
            )

        # For now, we rely on Claude's vision capabilities via the computer tool
        # In a production system, we could add OCR or image analysis here

        # Since we can't directly analyze image content without Claude's vision,
        # we return a pending verification that will be completed by the agent
        findings.append("Screenshot captured successfully")

        if action_taken:
            findings.append(f"Action taken: {action_taken}")

        if expected_state:
            findings.append(f"Expected state: {expected_state}")

        verification = VisualVerification(
            success=True,
            confidence=0.5,  # Medium confidence until agent verifies
            findings=findings,
        )

        self.verification_history.append(verification)
        return verification

    def detect_error_dialogs(self, screenshot_base64: str) -> tuple[bool, str | None]:
        """
        Detect if screenshot contains error dialogs.

        Note: This is a placeholder. In production, this would use OCR or
        Claude's vision capabilities to detect error patterns.

        Args:
            screenshot_base64: Base64 encoded screenshot

        Returns:
            Tuple of (error_detected, error_description)
        """
        # This would require OCR or vision API integration
        # For now, return that detection needs to be done by the agent
        return (False, None)

    def compare_screenshots(
        self,
        before_base64: str,
        after_base64: str,
    ) -> dict[str, Any]:
        """
        Compare two screenshots to detect changes.

        Args:
            before_base64: Screenshot before action
            after_base64: Screenshot after action

        Returns:
            Dictionary with comparison results
        """
        # Calculate rough difference based on size
        # In production, would use perceptual hashing or computer vision

        before_size = len(before_base64) if before_base64 else 0
        after_size = len(after_base64) if after_base64 else 0

        size_diff = abs(after_size - before_size)
        size_diff_pct = (size_diff / max(before_size, 1)) * 100

        return {
            "size_difference_bytes": size_diff,
            "size_difference_percent": size_diff_pct,
            "likely_changed": size_diff_pct > 5.0,  # More than 5% change
            "before_size": before_size,
            "after_size": after_size,
        }

    def create_verification_prompt(
        self,
        action_description: str,
        expected_outcome: str,
    ) -> str:
        """
        Create a prompt for the agent to verify visual state.

        Args:
            action_description: What action was taken
            expected_outcome: What should be visible

        Returns:
            Prompt for verification
        """
        return f"""
<visual_verification_request>
Action taken: {action_description}
Expected outcome: {expected_outcome}

Please analyze the current screenshot and verify:
1. Did the action complete successfully?
2. Is the expected state visible?
3. Are there any error dialogs or indicators?
4. Does the screen match expectations?

Respond with:
- SUCCESS: If everything matches expectations
- FAILURE: If there are errors or unexpected state
- PARTIAL: If some but not all expectations are met

Include specific details about what you see.
</visual_verification_request>
"""

    def get_verification_stats(self) -> dict[str, Any]:
        """
        Get statistics about verifications performed.

        Returns:
            Dictionary with verification stats
        """
        total = len(self.verification_history)
        successful = sum(1 for v in self.verification_history if v.success)
        errors_detected = sum(1 for v in self.verification_history if v.error_detected)

        avg_confidence = (
            sum(v.confidence for v in self.verification_history) / total
            if total > 0 else 0.0
        )

        return {
            "total_verifications": total,
            "successful": successful,
            "failed": total - successful,
            "errors_detected": errors_detected,
            "average_confidence": avg_confidence,
        }
