"""
Type definitions for LSP (Language Server Protocol) integration.
"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


class DiagnosticSeverity(int, Enum):
    """LSP diagnostic severity levels."""

    ERROR = 1
    WARNING = 2
    INFORMATION = 3
    HINT = 4


class LSPServerStatus(str, Enum):
    """Status of an LSP server."""

    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    ERROR = "error"


@dataclass
class Position:
    """Position in a document (0-indexed)."""

    line: int
    character: int

    def to_lsp(self) -> dict[str, int]:
        return {"line": self.line, "character": self.character}


@dataclass
class Range:
    """A range in a document."""

    start: Position
    end: Position

    def to_lsp(self) -> dict[str, Any]:
        return {"start": self.start.to_lsp(), "end": self.end.to_lsp()}


@dataclass
class Location:
    """A location in a document."""

    uri: str
    range: Range


@dataclass
class Diagnostic:
    """A diagnostic (error, warning, etc.)."""

    range: Range
    message: str
    severity: DiagnosticSeverity = DiagnosticSeverity.ERROR
    code: str | int | None = None
    source: str | None = None

    def format(self, file_path: str | None = None) -> str:
        """Format diagnostic for display."""
        severity_name = self.severity.name.lower()
        location = f"{file_path or 'unknown'}:{self.range.start.line + 1}:{self.range.start.character + 1}"
        source = f" [{self.source}]" if self.source else ""
        code = f" ({self.code})" if self.code else ""

        return f"{location}: {severity_name}{source}{code}: {self.message}"


@dataclass
class CompletionItem:
    """A completion suggestion."""

    label: str
    kind: int | None = None  # CompletionItemKind
    detail: str | None = None
    documentation: str | None = None
    insert_text: str | None = None


@dataclass
class Hover:
    """Hover information."""

    contents: str
    range: Range | None = None


@dataclass
class LSPServerConfig:
    """Configuration for an LSP server."""

    # Server name (unique identifier)
    name: str

    # Languages this server handles
    languages: list[str]

    # Command to start the server
    command: str

    # Arguments for the command
    args: list[str] = field(default_factory=list)

    # Environment variables
    env: dict[str, str] = field(default_factory=dict)

    # File extensions this server handles
    extensions: list[str] = field(default_factory=list)

    # Whether to auto-start this server
    auto_start: bool = True

    # Initialization options
    init_options: dict[str, Any] = field(default_factory=dict)

    # Whether this server is enabled
    enabled: bool = True


@dataclass
class LSPServerInfo:
    """Information about an LSP server."""

    name: str
    languages: list[str]
    status: LSPServerStatus = LSPServerStatus.STOPPED
    pid: int | None = None
    capabilities: dict[str, Any] = field(default_factory=dict)
    error: str | None = None
