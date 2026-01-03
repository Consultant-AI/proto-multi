"""
Proto LSP (Language Server Protocol) Integration Module.

Provides real-time code intelligence through Language Servers.

Supported Languages (default):
- Python (Pyright)
- TypeScript/JavaScript (typescript-language-server)
- Rust (rust-analyzer)
- Go (gopls)

Usage:
    from computer_use_demo.lsp import (
        get_lsp_manager,
        get_file_diagnostics,
        format_file_diagnostics,
    )

    # Get diagnostics for a file
    diagnostics = await get_file_diagnostics("main.py")

    # Format for display
    formatted = await format_file_diagnostics("main.py")
    print(formatted)

    # Use manager directly
    manager = get_lsp_manager()
    hover = await manager.get_hover(Path("main.py"), line=10, character=5)
"""

from .client import LSPClient

from .diagnostics import (
    check_file_for_errors,
    filter_errors,
    filter_warnings,
    format_diagnostics,
    format_diagnostics_summary,
    format_file_diagnostics,
    get_file_diagnostics,
)

from .manager import (
    DEFAULT_LSP_CONFIGS,
    LSPManager,
    get_lsp_manager,
    shutdown_lsp,
)

from .types import (
    CompletionItem,
    Diagnostic,
    DiagnosticSeverity,
    Hover,
    Location,
    LSPServerConfig,
    LSPServerInfo,
    LSPServerStatus,
    Position,
    Range,
)

__all__ = [
    # Types
    "CompletionItem",
    "Diagnostic",
    "DiagnosticSeverity",
    "Hover",
    "Location",
    "LSPServerConfig",
    "LSPServerInfo",
    "LSPServerStatus",
    "Position",
    "Range",
    # Client
    "LSPClient",
    # Manager
    "DEFAULT_LSP_CONFIGS",
    "LSPManager",
    "get_lsp_manager",
    "shutdown_lsp",
    # Diagnostics
    "check_file_for_errors",
    "filter_errors",
    "filter_warnings",
    "format_diagnostics",
    "format_diagnostics_summary",
    "format_file_diagnostics",
    "get_file_diagnostics",
]
