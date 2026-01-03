"""
Compliance Engine.

Regulatory compliance checking and management.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

from .types import (
    ComplianceRule,
    ComplianceCheck,
    ComplianceStatus,
)


class ComplianceEngine:
    """
    Regulatory compliance engine.

    Features:
    - Define compliance rules
    - Run compliance checks
    - Track compliance status
    - Generate compliance reports
    """

    def __init__(self, data_dir: Path | None = None):
        self._data_dir = data_dir or Path.home() / ".proto" / "company" / "business" / "compliance"
        self._data_dir.mkdir(parents=True, exist_ok=True)

        self._rules: dict[str, ComplianceRule] = {}
        self._checks: dict[str, ComplianceCheck] = {}
        self._check_functions: dict[str, Callable] = {}

        # Load built-in rules
        self._load_builtin_rules()
        self._load()

    def _load_builtin_rules(self) -> None:
        """Load built-in compliance rules."""
        builtin_rules = [
            # GDPR Rules
            ComplianceRule(
                id="gdpr-consent",
                name="GDPR Consent",
                description="User consent must be obtained before processing personal data",
                category="gdpr",
                severity="error",
            ),
            ComplianceRule(
                id="gdpr-data-retention",
                name="GDPR Data Retention",
                description="Personal data should not be retained longer than necessary",
                category="gdpr",
                severity="warning",
            ),
            ComplianceRule(
                id="gdpr-right-to-erasure",
                name="GDPR Right to Erasure",
                description="Users must be able to request deletion of their data",
                category="gdpr",
                severity="error",
            ),
            # SOC2 Rules
            ComplianceRule(
                id="soc2-access-control",
                name="SOC2 Access Control",
                description="Access to systems must be properly controlled",
                category="soc2",
                severity="error",
            ),
            ComplianceRule(
                id="soc2-encryption",
                name="SOC2 Encryption",
                description="Data must be encrypted at rest and in transit",
                category="soc2",
                severity="error",
            ),
            ComplianceRule(
                id="soc2-audit-logging",
                name="SOC2 Audit Logging",
                description="All system access and changes must be logged",
                category="soc2",
                severity="warning",
            ),
            # Security Rules
            ComplianceRule(
                id="security-no-secrets",
                name="No Secrets in Code",
                description="API keys, passwords, and secrets must not be in source code",
                category="security",
                severity="error",
            ),
            ComplianceRule(
                id="security-https",
                name="HTTPS Required",
                description="All network communication must use HTTPS",
                category="security",
                severity="error",
            ),
        ]

        for rule in builtin_rules:
            self._rules[rule.id] = rule

    def _load(self) -> None:
        """Load custom rules and check history from disk."""
        rules_file = self._data_dir / "custom_rules.json"
        if rules_file.exists():
            try:
                with open(rules_file, "r") as f:
                    data = json.load(f)
                for rule_data in data:
                    rule = ComplianceRule(
                        id=rule_data["id"],
                        name=rule_data["name"],
                        description=rule_data.get("description", ""),
                        category=rule_data.get("category", "custom"),
                        severity=rule_data.get("severity", "warning"),
                    )
                    self._rules[rule.id] = rule
            except Exception:
                pass

    def _save(self) -> None:
        """Save custom rules to disk."""
        rules_file = self._data_dir / "custom_rules.json"
        custom_rules = [
            {
                "id": r.id,
                "name": r.name,
                "description": r.description,
                "category": r.category,
                "severity": r.severity,
            }
            for r in self._rules.values()
            if r.category == "custom"
        ]
        with open(rules_file, "w") as f:
            json.dump(custom_rules, f, indent=2)

    # Rule management

    def add_rule(
        self,
        rule_id: str,
        name: str,
        description: str,
        category: str = "custom",
        severity: str = "warning",
        check_function: Callable | None = None,
    ) -> ComplianceRule:
        """Add a custom compliance rule."""
        rule = ComplianceRule(
            id=rule_id,
            name=name,
            description=description,
            category=category,
            severity=severity,
        )

        self._rules[rule.id] = rule

        if check_function:
            self._check_functions[rule.id] = check_function

        self._save()
        print(f"[Compliance] Added rule: {name}")
        return rule

    def get_rule(self, rule_id: str) -> ComplianceRule | None:
        """Get a rule by ID."""
        return self._rules.get(rule_id)

    def list_rules(
        self,
        category: str | None = None,
        enabled_only: bool = True,
    ) -> list[ComplianceRule]:
        """List compliance rules."""
        rules = list(self._rules.values())

        if category:
            rules = [r for r in rules if r.category == category]
        if enabled_only:
            rules = [r for r in rules if r.enabled]

        return rules

    def enable_rule(self, rule_id: str) -> bool:
        """Enable a rule."""
        rule = self._rules.get(rule_id)
        if rule:
            rule.enabled = True
            return True
        return False

    def disable_rule(self, rule_id: str) -> bool:
        """Disable a rule."""
        rule = self._rules.get(rule_id)
        if rule:
            rule.enabled = False
            return True
        return False

    # Compliance checking

    async def check_rule(
        self,
        rule_id: str,
        context: dict[str, Any] | None = None,
        checked_by: str = "system",
    ) -> ComplianceCheck:
        """Run a compliance check for a specific rule."""
        rule = self._rules.get(rule_id)
        if not rule:
            return ComplianceCheck(
                rule_id=rule_id,
                status=ComplianceStatus.REVIEW_NEEDED,
                details="Rule not found",
                checked_by=checked_by,
            )

        # Run check function if available
        check_fn = self._check_functions.get(rule_id)
        if check_fn:
            try:
                result = check_fn(context or {})
                status = ComplianceStatus.COMPLIANT if result else ComplianceStatus.NON_COMPLIANT
                details = "Check passed" if result else "Check failed"
            except Exception as e:
                status = ComplianceStatus.REVIEW_NEEDED
                details = f"Check error: {e}"
        else:
            # Manual review needed
            status = ComplianceStatus.REVIEW_NEEDED
            details = "Manual review required"

        check = ComplianceCheck(
            rule_id=rule_id,
            status=status,
            details=details,
            checked_by=checked_by,
        )

        self._checks[check.id] = check
        return check

    async def check_category(
        self,
        category: str,
        context: dict[str, Any] | None = None,
        checked_by: str = "system",
    ) -> list[ComplianceCheck]:
        """Run all checks for a category."""
        rules = self.list_rules(category=category)
        checks = []

        for rule in rules:
            check = await self.check_rule(rule.id, context, checked_by)
            checks.append(check)

        return checks

    async def check_all(
        self,
        context: dict[str, Any] | None = None,
        checked_by: str = "system",
    ) -> list[ComplianceCheck]:
        """Run all enabled compliance checks."""
        rules = self.list_rules(enabled_only=True)
        checks = []

        for rule in rules:
            check = await self.check_rule(rule.id, context, checked_by)
            checks.append(check)

        return checks

    # Manual review

    async def mark_compliant(
        self,
        rule_id: str,
        evidence: list[str] | None = None,
        reviewer: str = "",
    ) -> ComplianceCheck:
        """Manually mark a rule as compliant."""
        check = ComplianceCheck(
            rule_id=rule_id,
            status=ComplianceStatus.COMPLIANT,
            details="Manually verified as compliant",
            evidence=evidence or [],
            checked_by=reviewer,
        )

        self._checks[check.id] = check
        print(f"[Compliance] Rule {rule_id} marked compliant")
        return check

    async def mark_non_compliant(
        self,
        rule_id: str,
        details: str,
        reviewer: str = "",
    ) -> ComplianceCheck:
        """Manually mark a rule as non-compliant."""
        check = ComplianceCheck(
            rule_id=rule_id,
            status=ComplianceStatus.NON_COMPLIANT,
            details=details,
            checked_by=reviewer,
        )

        self._checks[check.id] = check
        print(f"[Compliance] Rule {rule_id} marked non-compliant: {details}")
        return check

    # Reporting

    def get_compliance_status(self) -> dict[str, Any]:
        """Get overall compliance status."""
        rules = self.list_rules(enabled_only=True)
        checks = list(self._checks.values())

        # Get latest check for each rule
        latest_checks = {}
        for check in sorted(checks, key=lambda c: c.checked_at):
            latest_checks[check.rule_id] = check

        compliant = sum(1 for c in latest_checks.values() if c.status == ComplianceStatus.COMPLIANT)
        non_compliant = sum(1 for c in latest_checks.values() if c.status == ComplianceStatus.NON_COMPLIANT)
        review_needed = sum(1 for c in latest_checks.values() if c.status == ComplianceStatus.REVIEW_NEEDED)
        not_checked = len(rules) - len(latest_checks)

        return {
            "total_rules": len(rules),
            "compliant": compliant,
            "non_compliant": non_compliant,
            "review_needed": review_needed,
            "not_checked": not_checked,
            "compliance_rate": compliant / len(rules) if rules else 0,
        }

    def get_compliance_report(
        self,
        category: str | None = None,
    ) -> dict[str, Any]:
        """Generate a detailed compliance report."""
        rules = self.list_rules(category=category)
        checks = list(self._checks.values())

        # Get latest check for each rule
        latest_checks = {}
        for check in sorted(checks, key=lambda c: c.checked_at):
            latest_checks[check.rule_id] = check

        report_items = []
        for rule in rules:
            check = latest_checks.get(rule.id)
            report_items.append({
                "rule_id": rule.id,
                "rule_name": rule.name,
                "category": rule.category,
                "severity": rule.severity,
                "status": check.status.value if check else "not_checked",
                "details": check.details if check else "",
                "last_checked": check.checked_at.isoformat() if check else None,
            })

        return {
            "generated_at": datetime.utcnow().isoformat(),
            "category": category or "all",
            "summary": self.get_compliance_status(),
            "items": report_items,
        }


# Global instance
_compliance_engine: ComplianceEngine | None = None


def get_compliance_engine() -> ComplianceEngine:
    """Get or create the global compliance engine."""
    global _compliance_engine
    if _compliance_engine is None:
        _compliance_engine = ComplianceEngine()
    return _compliance_engine
