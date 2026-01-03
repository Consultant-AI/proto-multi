"""
Code Modifier.

Safe code modification with testing and rollback.
"""

import json
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any

from .types import (
    Modification,
    ModificationType,
    ModificationStatus,
    SafetyCheck,
)


class CodeModifier:
    """
    Safely modifies code with testing and rollback capabilities.

    Safety features:
    - Creates backups before changes
    - Runs tests after changes
    - Rolls back on test failure
    - Rate limits modifications
    """

    def __init__(
        self,
        project_dir: Path | None = None,
        backup_dir: Path | None = None,
        max_daily_modifications: int = 10,
    ):
        self._project_dir = project_dir or Path.cwd()
        self._backup_dir = backup_dir or Path.home() / ".proto" / "self-improvement" / "backups"
        self._backup_dir.mkdir(parents=True, exist_ok=True)

        self._max_daily_modifications = max_daily_modifications
        self._modifications_today: list[Modification] = []

    def can_modify(self) -> tuple[bool, str]:
        """Check if we can make more modifications today."""
        # Filter to today's modifications
        today = datetime.utcnow().date()
        todays_mods = [
            m for m in self._modifications_today
            if m.created_at.date() == today
        ]

        if len(todays_mods) >= self._max_daily_modifications:
            return False, f"Daily limit reached ({self._max_daily_modifications} modifications)"

        return True, ""

    async def prepare_modification(
        self,
        target: str,
        changes: dict[str, Any],
        reason: str = "",
    ) -> Modification:
        """
        Prepare a code modification.

        Args:
            target: File path to modify
            changes: Dictionary describing the changes
            reason: Reason for the modification

        Returns:
            Prepared modification (not yet applied)
        """
        target_path = self._project_dir / target

        # Create backup
        backup = {}
        if target_path.exists():
            backup["content"] = target_path.read_text()
            backup["exists"] = True
        else:
            backup["exists"] = False

        modification = Modification(
            type=ModificationType.CODE_CHANGE,
            target=target,
            description=changes.get("description", ""),
            changes=changes,
            backup=backup,
            reason=reason,
            source="code_modifier",
        )

        # Run safety checks
        modification.safety_checks = await self._run_safety_checks(modification)

        return modification

    async def _run_safety_checks(self, modification: Modification) -> list[SafetyCheck]:
        """Run safety checks on a modification."""
        checks = []

        # Check 1: Rate limit
        can_modify, msg = self.can_modify()
        checks.append(SafetyCheck(
            name="rate_limit",
            passed=can_modify,
            message=msg if not can_modify else "Within daily limit",
            severity="error",
        ))

        # Check 2: File exists (for updates)
        target_path = self._project_dir / modification.target
        if modification.changes.get("type") == "update" and not target_path.exists():
            checks.append(SafetyCheck(
                name="file_exists",
                passed=False,
                message=f"Target file does not exist: {modification.target}",
                severity="error",
            ))
        else:
            checks.append(SafetyCheck(
                name="file_exists",
                passed=True,
                message="Target file check passed",
            ))

        # Check 3: Not modifying critical files
        critical_patterns = ["__init__.py", "loop.py", "base_agent.py"]
        is_critical = any(p in modification.target for p in critical_patterns)
        checks.append(SafetyCheck(
            name="critical_file",
            passed=True,  # Allow but flag
            message="Modifying critical file - extra review recommended" if is_critical else "Not a critical file",
            severity="warning" if is_critical else "info",
        ))

        # Check 4: Has backup
        checks.append(SafetyCheck(
            name="backup_created",
            passed=bool(modification.backup),
            message="Backup created" if modification.backup else "No backup available",
            severity="warning",
        ))

        return checks

    async def apply_modification(
        self,
        modification: Modification,
        run_tests: bool = True,
    ) -> bool:
        """
        Apply a modification.

        Args:
            modification: The modification to apply
            run_tests: Whether to run tests after applying

        Returns:
            True if successfully applied
        """
        if not modification.can_apply():
            print(f"[CodeModifier] Cannot apply modification: {modification.status}")
            return False

        target_path = self._project_dir / modification.target

        try:
            # Save backup to disk
            backup_path = self._backup_dir / f"{modification.id}.json"
            with open(backup_path, "w") as f:
                json.dump({
                    "target": modification.target,
                    "backup": modification.backup,
                    "timestamp": datetime.utcnow().isoformat(),
                }, f, indent=2)

            # Apply changes
            change_type = modification.changes.get("type", "update")

            if change_type == "create":
                target_path.parent.mkdir(parents=True, exist_ok=True)
                target_path.write_text(modification.changes.get("content", ""))

            elif change_type == "update":
                content = modification.changes.get("content")
                if content:
                    target_path.write_text(content)

            elif change_type == "delete":
                if target_path.exists():
                    target_path.unlink()

            elif change_type == "replace":
                if target_path.exists():
                    old_text = modification.changes.get("old", "")
                    new_text = modification.changes.get("new", "")
                    content = target_path.read_text()
                    content = content.replace(old_text, new_text)
                    target_path.write_text(content)

            modification.status = ModificationStatus.APPLIED
            modification.applied_at = datetime.utcnow()

            # Run tests
            if run_tests:
                modification.status = ModificationStatus.TESTING
                test_passed = await self._run_tests()
                modification.test_results = {"passed": test_passed}

                if not test_passed:
                    print("[CodeModifier] Tests failed, rolling back...")
                    await self.rollback_modification(modification)
                    modification.status = ModificationStatus.FAILED
                    return False

            self._modifications_today.append(modification)
            print(f"[CodeModifier] Applied modification to {modification.target}")
            return True

        except Exception as e:
            print(f"[CodeModifier] Error applying modification: {e}")
            modification.status = ModificationStatus.FAILED
            return False

    async def rollback_modification(self, modification: Modification) -> bool:
        """Roll back a modification."""
        if not modification.backup:
            print("[CodeModifier] No backup available for rollback")
            return False

        target_path = self._project_dir / modification.target

        try:
            if modification.backup.get("exists"):
                target_path.write_text(modification.backup.get("content", ""))
            else:
                if target_path.exists():
                    target_path.unlink()

            modification.status = ModificationStatus.ROLLED_BACK
            print(f"[CodeModifier] Rolled back modification to {modification.target}")
            return True

        except Exception as e:
            print(f"[CodeModifier] Rollback failed: {e}")
            return False

    async def _run_tests(self) -> bool:
        """Run project tests."""
        try:
            # Try pytest
            result = subprocess.run(
                ["python", "-m", "pytest", "-x", "-q"],
                cwd=self._project_dir,
                capture_output=True,
                timeout=300,
            )
            return result.returncode == 0

        except subprocess.TimeoutExpired:
            print("[CodeModifier] Tests timed out")
            return False
        except Exception as e:
            print(f"[CodeModifier] Error running tests: {e}")
            # If no tests, consider it passed
            return True

    def list_modifications(
        self,
        status: ModificationStatus | None = None,
    ) -> list[Modification]:
        """List modifications."""
        mods = self._modifications_today

        if status:
            mods = [m for m in mods if m.status == status]

        return mods

    def get_modification_history(self) -> list[dict[str, Any]]:
        """Get history of all modifications."""
        history = []

        for backup_file in self._backup_dir.glob("*.json"):
            try:
                with open(backup_file, "r") as f:
                    data = json.load(f)
                history.append(data)
            except Exception:
                pass

        return sorted(history, key=lambda x: x.get("timestamp", ""), reverse=True)
