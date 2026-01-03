"""
Diagnostics formatting and utilities.
"""

from pathlib import Path

from .manager import get_lsp_manager
from .types import Diagnostic, DiagnosticSeverity


def format_diagnostics(
    diagnostics: list[Diagnostic],
    file_path: str | Path | None = None,
    include_severity: bool = True,
) -> str:
    """
    Format diagnostics for display.

    Args:
        diagnostics: List of diagnostics
        file_path: File path for context
        include_severity: Whether to include severity in output

    Returns:
        Formatted string
    """
    if not diagnostics:
        return ""

    file_str = str(file_path) if file_path else None

    lines = []
    for diag in sorted(diagnostics, key=lambda d: (d.severity.value, d.range.start.line)):
        lines.append(diag.format(file_str))

    return "\n".join(lines)


def format_diagnostics_summary(diagnostics: list[Diagnostic]) -> str:
    """
    Format a summary of diagnostics.

    Args:
        diagnostics: List of diagnostics

    Returns:
        Summary string (e.g., "3 errors, 2 warnings")
    """
    if not diagnostics:
        return "No issues"

    counts = {
        DiagnosticSeverity.ERROR: 0,
        DiagnosticSeverity.WARNING: 0,
        DiagnosticSeverity.INFORMATION: 0,
        DiagnosticSeverity.HINT: 0,
    }

    for diag in diagnostics:
        counts[diag.severity] += 1

    parts = []
    if counts[DiagnosticSeverity.ERROR]:
        parts.append(f"{counts[DiagnosticSeverity.ERROR]} error(s)")
    if counts[DiagnosticSeverity.WARNING]:
        parts.append(f"{counts[DiagnosticSeverity.WARNING]} warning(s)")
    if counts[DiagnosticSeverity.INFORMATION]:
        parts.append(f"{counts[DiagnosticSeverity.INFORMATION]} info")
    if counts[DiagnosticSeverity.HINT]:
        parts.append(f"{counts[DiagnosticSeverity.HINT]} hint(s)")

    return ", ".join(parts) if parts else "No issues"


def filter_errors(diagnostics: list[Diagnostic]) -> list[Diagnostic]:
    """Filter to only error-level diagnostics."""
    return [d for d in diagnostics if d.severity == DiagnosticSeverity.ERROR]


def filter_warnings(diagnostics: list[Diagnostic]) -> list[Diagnostic]:
    """Filter to only warning-level diagnostics."""
    return [d for d in diagnostics if d.severity == DiagnosticSeverity.WARNING]


async def get_file_diagnostics(path: Path | str) -> list[Diagnostic]:
    """
    Get diagnostics for a file.

    Convenience function that uses the global manager.

    Args:
        path: File path

    Returns:
        List of diagnostics
    """
    if isinstance(path, str):
        path = Path(path)

    manager = get_lsp_manager()
    return await manager.get_diagnostics(path)


async def format_file_diagnostics(path: Path | str) -> str:
    """
    Get and format diagnostics for a file.

    Args:
        path: File path

    Returns:
        Formatted diagnostics string
    """
    if isinstance(path, str):
        path = Path(path)

    diagnostics = await get_file_diagnostics(path)
    return format_diagnostics(diagnostics, path)


async def check_file_for_errors(path: Path | str) -> tuple[bool, str]:
    """
    Check if a file has errors.

    Args:
        path: File path

    Returns:
        Tuple of (has_errors, formatted_diagnostics)
    """
    if isinstance(path, str):
        path = Path(path)

    diagnostics = await get_file_diagnostics(path)
    errors = filter_errors(diagnostics)

    has_errors = len(errors) > 0
    formatted = format_diagnostics(errors, path) if has_errors else ""

    return has_errors, formatted
